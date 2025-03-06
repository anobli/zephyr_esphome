from dataclasses import fields
import hashlib
import re
from actions.action import UnsupportedTypeError, get_automation_action_keys, get_automation_condition_keys


def indent(format, indent_level):
    indent = ""
    for i in range(0, indent_level):
        indent += "\t"
    return indent + format

def get_args(args):
    c = ""
    for field in fields(args):
        if field.type == str:
            value = getattr(args, field.name)
            if value is None:
                c += "NULL,"
            else:
                c += "\"{}\",".format(value)
        elif field.type == list:
            if "c" not in field.metadata:
                raise UnsupportedTypeError(field.name)
            
            # Not sure if this is strictly required
            # Maybe we can assume that a list is always vargs
            c_metadata = field.metadata["c"]
            if not c_metadata.is_vargs():
                raise UnsupportedTypeError(field.name)
            vargs = getattr(args, field.name)
            if vargs:
                # This is expected to be a list of lamba
                # This should already be C / C++ code
                for varg in vargs:
                    c += "\"{}\",".format(varg)
            
        else:
            c += "{},".format(getattr(args, field.name))
    return c[0:-1]

def do_generate_function_call(action, indent_level=0):
    c = ""
    supported_actions = get_automation_action_keys()
    for action_name in supported_actions:
        if getattr(action, action_name):
            args = getattr(action, action_name)
            c += indent("esphome_{}({});\n", indent_level + 1).format(action_name, get_args(args))
    return c

def do_generate_condition_function_call(condition):
    c = ""
    supported_conditions = get_automation_condition_keys()
    for condition_name in supported_conditions:
        if getattr(condition, condition_name):
            arg = getattr(condition, condition_name)
            c += "esphome_{}({})".format(condition_name, arg)
    return c


def do_generate_if_statement(action, indent_level=0):
    c = ""
    conditions = []
    condition_type = None
    for tmp in ["k_or", "k_and"]:
        condition_list = getattr(action.k_if.condition, tmp)
        if condition_list:
            condition_type = tmp
            for condition in condition_list:
                conditions.append(do_generate_condition_function_call(condition))

    c += indent("if(", indent_level + 1)
    for condition in conditions:
        c += condition
        if condition_type == "k_or":
            c += "||"
        if condition_type == "k_and":
            c += "&&"
    c = c[0:-2]
    c += "){\n"
    if action.k_if.k_then:
        for then_action in action.k_if.k_then:
            c += do_generate_function_call(then_action, indent_level + 1)
    if action.k_if.k_else:
        c += indent("} else {\n", indent_level + 1)
        for then_action in action.k_if.k_else:
            c += do_generate_function_call(then_action, indent_level + 1)
    c += indent("}\n", indent_level + 1)

    return c

def do_generate_action_content(component_name, component, field):
    actions = getattr(component, field.name)
    c = "{\n"
    for action in actions:
        for then_action in action.k_then:
            if then_action.k_if is not None:
                c += do_generate_if_statement(then_action)
            else:
                c += do_generate_function_call(then_action)
    c += "}\n"
    return c

def do_generate_action_function_name(component_name, component, field):
    content = do_generate_action_content(component_name, component, field)
    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    return "esphome_{}_{}_{}".format(component_name, field.name, content_hash)
