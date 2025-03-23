import re
import sys
import argparse
import glob
from pathlib import Path
from subprocess import call

from string import Template

# Generate with
# protoc --python_out=script/api_protobuf -I esphome/components/api/ api_options.proto
import aioesphomeapi.api_options_pb2 as pb
import google.protobuf.descriptor_pb2 as descriptor

import configparser

from jinja2 import Environment, FileSystemLoader

SOURCE_BOTH = 0
SOURCE_SERVER = 1
SOURCE_CLIENT = 2

template_conf_variables = {
    'project' :{
        'doc': 'Name of project',
        'default': None,
    },
    'prefix' :{
        'doc': 'Prefix for functions or files',
        'default': "${project}_",
    },
    'function_prefix': {
        'doc': 'Default function prefix, applied to all functions unless specific function prefix is defined',
        'default': "${prefix}",
    },
    'file_prefix': {
        'doc': 'Output file name prefix, applied to all generated files unless a specific prefix is defined for the a file',
        'default': "${prefix}",
    },
    'rpc_data_type': {
        'doc': 'Define the type of the variable used to store rpc data',
        'default': "uint8_t *",
    },
    'rpc_data_name': {
        'doc': 'Define the name of the variable used to store rpc data',
        'default': "data",
    },
    'rpc_data_def': {
        'doc': 'Helper to use rpc_data_type and rpc_data_name',
        'default': "${rpc_data_type} ${rpc_data_name}",
    },
    'rpc_len_type': {
        'doc': 'Define the type of the variable used to store rpc data length',
        'default': "size_t",
    },
    'rpc_len_name': {
        'doc': 'Define the name of the variable used to store rpc data length',
        'default': "len",
    },
    'rpc_len_def': {
        'doc': 'Helper to use rpc_len_type and rpc_len_name',
        'default': "${rpc_len_type} ${rpc_len_name}",
    },
    'user_data_type': {
        'doc': 'User data type',
        'default': "void *",
    },
    'user_data_name': {
        'doc': 'User data name',
        'default': "user_data",
    },
    'user_data_def': {
        'doc': 'Helper to use user_data_type and user_data_name',
        'default': "${user_data_type} ${user_data_name}",
    },
    'msg_data_type': {
        'doc': 'The type used to declare a message pointer',
        'default' : "${msg_name} *",
    },
    'msg_data_name': {
        'doc': 'The name of the message pointer',
        'default' : "msg",
    },
    'msg_data_def': {
        'doc': 'Helper to use msg_data_type and msg_data_name',
        'default' : "${msg_data_type} ${msg_data_name}",
    },
    'msg_dump_function_name': {
        'doc': 'Name of the dump function, used to print the content of a message',
        'default': "${function_prefix}${msg_name}Dump",
    },
    'msg_read_function_name': {
        'doc': 'Name of the read function that convert raw data to message and call the cb function',
        'default': "${function_prefix}${msg_name}Read",
    },
    'msg_cb_function_name': {
        'doc': 'Name of the cb function that should defined by user to handle the message',
        'default': "${function_prefix}${msg_name}Cb",
    },
    'msg_write_function_name': {
        'doc': 'Name of the write function that should used byuser to send a message',
        'default': "${function_prefix}${msg_name}Write",
    },
    'pb_c_unpack_function_name': {
        'doc': 'Protobuf-c unpack function name',
        'default': None,
    },
    'pb_c_free_unpacked_function_name': {
        'doc': 'Protobuf-c free_unpacked function name',
        'default': None,
    },
    'pb_c_get_size_function_name': {
        'doc': 'Protobuf-c get_size function name',
        'default': None,
    },
}

template_variables = {
    'pb_header': {
        'doc' : 'Name of the header generated using protobuf',
        'default': None,
    },
    'protobuf_c_allocator_name': {
        'doc': 'Name of the protobuf allocator',
        'default': None,
    },
    'platform_send_name': {
        'doc': 'Name of function that send raw data', # Remove me
        'default': None,
    },
}

def protobuf_function_name(name, function):
    result = re.findall(r"([A-Z]+[a-z]*)", name)
    base = ""
    for word in result:
        base += word.lower() + "_"
    return base + function

def get_opt(desc, opt, default=None):
    if not desc.options.HasExtension(opt):
        return default
    return desc.options.Extensions[opt]

def generate_d(variables, d = {}):
    for key in variables:
        d[key] = variables[key]["default"]
    return d

def config_to_d(config, d):
    for key in config["Global"]:
        if key not in d:
            print(f"Warning: unsupported variable {key}")
        d[key] = config["Global"][key]

    d["user_data_arg"] = f"{d['user_data_type']} {d['user_data_name']}"
    d["rpc_data_arg"] = f"{d['rpc_data_type']} {d['rpc_data_name']}"
    d["rpc_len_arg"] = f"{d['rpc_len_type']} {d['rpc_len_name']}"

    return d

def config_file_to_d(config, tpl_file, d):
    if tpl_file in config:
        for key in config[tpl_file]:
            value = config[tpl_file][key]
            if value is None:
                value = ""
            d[key] = value
    return d

def args_to_d(args, d):
    for key in d:
        if hasattr(args, key) and getattr(args, key):
            d[key] = getattr(args, key)
    return d

def substitute_d(d):
    found = False
    for key in d:
        txt = d[key]
        if "${msg_name}" in str(txt):
            continue
        if "$" in str(txt):
            found = True
            tpl = Template(txt)
            d[key] = tpl.substitute(d)
    return found

def rsubstitute_d(d):
    while True:
        if substitute_d(d) == False:
            break
    return d

def rsubstitute(txt, d):
    while "$" in txt:
        tpl = Template(txt)
        txt = tpl.substitute(d)
    return txt

def finish_d(d):
    d["PROJECT"] = d["project"].upper()
    # TODO: make prefix unique, add somthing like protobuf file name
    d["PREFIX"] = d["PROJECT"] + "_"
    d["protobuf_c_allocator_name"] = "${function_prefix}pb_allocator"
    d["platform_send_name"] = "${function_prefix}rpc_send"

#    return d
    return rsubstitute_d(d)

class ProtoC:
    def __init__(self, out, include_dir=[]):
        self.out = out
        self.include_dir = include_dir

    def protoc(self, input_files=[]):
        call(["mkdir", "-p", self.out])
        prot_file = self.out / "tmp.protoc"
        protoc_args = ["protoc", "-o", str(prot_file)]
        if self.include_dir:
            for include_dir in self.include_dir:
                protoc_args.append("-I")
                protoc_args.append(str(include_dir))
        for input_file in input_files:
            protoc_args.append(input_file)
        call(protoc_args)
        proto_content = prot_file.read_bytes()
        desc = descriptor.FileDescriptorSet.FromString(proto_content)
        dependencies = set(input_files)
        for file in desc.file:
            if file.dependency:
                for dep in file.dependency:
                    dependencies.add(dep)
        input_set = set(input_files)
        if input_set != dependencies:
            return self.run(dependencies)
        prot_file.unlink()
        return desc, dependencies

    def protoc_c(self, protofiles):
        protoc_c_args = ["protoc-c", f"--c_out={str(self.out)}"]
        if self.include_dir:
            for include_dir in self.include_dir:
                protoc_c_args.append("-I")
                protoc_c_args.append(str(include_dir))
        for input_file in protofiles:
            protoc_c_args.append(input_file)
        call(protoc_c_args)

def protoc(args, input_files=[]):
    call(["mkdir", "-p", args.out])
    prot_file = args.out / "tmp.protoc"
    protoc_args = ["protoc", "-o", str(prot_file)]
    if args.include_dir:
        for include_dir in args.include_dir:
            protoc_args.append("-I")
            protoc_args.append(str(include_dir))
    for input_file in input_files:
        protoc_args.append(input_file)
    call(protoc_args)
    proto_content = prot_file.read_bytes()
    desc = descriptor.FileDescriptorSet.FromString(proto_content)
    dependencies = set(input_files)
    for file in desc.file:
        if file.dependency:
            for dep in file.dependency:
                dependencies.add(dep)
    input_set = set(input_files)
    if input_set != dependencies:
        return protoc(args, dependencies)
    prot_file.unlink()
    return desc, dependencies

def generate(args, tpl_dir=None, clang_format_file=None):
    cwd = Path(__file__).resolve().parent
    if not tpl_dir:
        tpl_dir = cwd / "templates" / args.platform
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read([tpl_dir / "platform.conf"])

    d = generate_d(template_conf_variables)
    d = generate_d(template_variables, d)
    d = config_to_d(config, d)
    d = args_to_d(args, d)
    d = finish_d(d)

    call(["mkdir", "-p", args.out])
    desc, protofiles = protoc(args, args.protofile)

    if not args.skip_protobuf_c:
        protoc_c_args = ["protoc-c", f"--c_out={str(args.out)}"]
        if args.include_dir:
            for include_dir in args.include_dir:
                protoc_c_args.append("-I")
                protoc_c_args.append(str(include_dir))
        for input_file in protofiles:
            protoc_c_args.append(input_file)
        call(protoc_c_args)

    if args.server:
        input_sources = (SOURCE_BOTH, SOURCE_SERVER)
        output_sources = (SOURCE_BOTH, SOURCE_CLIENT)
    else:
        input_sources = (SOURCE_BOTH, SOURCE_CLIENT)
        output_sources = (SOURCE_BOTH, SOURCE_SERVER)

    environment = Environment(loader=FileSystemLoader(tpl_dir))

    for protofile in args.protofile:
        for file in desc.file:
            if file.name == protofile:
                for tpl_file in tpl_dir.glob("*"):
                    tpl_filename = str(tpl_file).split("/")[-1]
                    if tpl_filename == "platform.conf":
                        continue
                    template = environment.get_template(tpl_filename)
                    messages = []

                    e = config_file_to_d(config, tpl_filename, d.copy())
                    for mt in file.message_type:
                        id_ = get_opt(mt, pb.id)
                        if not id_:
                            continue

                        if mt.field:
                            e["has_field"] = True
                        else:
                            e["has_field"] = False
                        e["msg_name"] = mt.name
                        fields = []
                        for field in mt.field:
                            fields.append({
                                "name": field.name,
                                "type": field.type,
                                "type_name": field.type_name,
                                "value": f"msg->{field.name}"
                            })
                        messages.append({
                            "name": mt.name,
                            "msg_data_type": rsubstitute(e["msg_data_type"], e), 
                            "msg_data_name": rsubstitute(e["msg_data_name"], e),
                            "msg_data_def": rsubstitute(e["msg_data_def"], e),
                            "id": get_opt(mt, pb.id),
                            "field": fields,
                            'msg_dump_function_name': rsubstitute(e["msg_dump_function_name"], e),
                            'msg_cb_function_name': rsubstitute(e["msg_cb_function_name"], e),
                            'msg_read_function_name': rsubstitute(e["msg_read_function_name"], e),
                            'msg_write_function_name': rsubstitute(e["msg_write_function_name"], e),
                            'pb_c_unpack_function_name': protobuf_function_name(mt.name, "_unpack"),
                            'pb_c_free_unpacked_function_name': protobuf_function_name(mt.name, "_free_unpacked"),
                            'pb_c_get_size_function_name': protobuf_function_name(mt.name, "_get_packed_size"),
                            'pb_c_pack_function_name': protobuf_function_name(mt.name, "_pack"),

                        })
                    f = rsubstitute_d(e.copy())
                    proto_name = file.name.split(".")[0]
                    f["pb_header"] = f"{proto_name}.pb-c.h"
                    f["read_function_prefix"] = f["function_prefix"]
                    f["messages"] = list(messages)
                    content = template.render(f)

                    tpl = Template(e[f"file_prefix"])
                    file_prefix = tpl.substitute(f)
                    f = open(args.out / (file_prefix + tpl_filename), "w")
                    f.write(content)
                    f.close()

    files = []
    files += glob.glob(str(args.out) + "**/*.h")
    files += glob.glob(str(args.out) + "**/*.c")


    for file in files:
        print ("Formating {}".format(file))
        clang_format_args = ['clang-format', '-i', file]
        if clang_format_file:
            clang_format_args += ['--style', 'file:{}'.format(clang_format_file)]
        call(clang_format_args)

def setup_parser():
    parser = argparse.ArgumentParser(description='Generate RPC and useful functions from protobuf files')
    parser.add_argument('protofile', metavar='protofile', nargs='+',
                        help='protobuf file to use')
    parser.add_argument('-I', dest='include_dir', action='append',
                        type=Path, help='Path of protobuf files (sources and dependencies)')
    parser.add_argument('-O', dest='out', type=Path, default=Path("out"))
    parser.add_argument('--platform', default="zephyr")
    parser.add_argument('--server', action=argparse.BooleanOptionalAction)
    parser.add_argument('--skip-protobuf-c', action=argparse.BooleanOptionalAction)
    parser.add_argument('--disable-dump', action=argparse.BooleanOptionalAction)

    for variable in template_conf_variables:
        parser.add_argument(f"--{variable}", help=template_conf_variables[variable])
    return parser

def main():
    parser = setup_parser()
    args = parser.parse_args()
    generate(args)

if __name__ == "__main__":
    sys.exit(main())
