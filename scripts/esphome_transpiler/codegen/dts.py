from dataclasses import fields
from codegen.action_common import do_generate_action_function_name
from codegen.codegen import CodeComponentBase, CodeGen

import hashlib

from esphome_const import ESPHOME_AUTOMATION, ESPHOME_PIN, ESPHOME_TIME
from soc import get_soc

def indent(format, indent_level):
    indent = ""
    for i in range(0, indent_level):
        indent += "\t"
    return indent + format

class DTSNode:
    def __init__(self, name, component):
        self.child = []
        self.name = name
        self.value = component
        self.compatible = None
        if component is not None:
            self.compatible = component.dts_compatible()
    
    def to_string(self, indent_level):
        node = indent("{}{{\n", indent_level).format(self.name, indent_level)
        if self.compatible:
            node += indent("compatible=\"{}\";\n", indent_level + 1).format(self.compatible)
        if self.value:
            for field in fields(self.value):
                if "dts" not in field.metadata:
                    continue
                dts_prop = DTSProperty(self, self.value, field)
                dts_prop_string = dts_prop.to_string(indent_level + 1)
                if dts_prop_string:
                    node += dts_prop_string

        for child in self.child:
            node += child.to_string(indent_level + 1)

        node += indent("};\n", indent_level)
        return node

    def add_child(self, child):
        self.child.append(child)

class DTSRoot(DTSNode):
    def __init__(self):
        super().__init__("/", None)
    
    def to_string(self):
        return super().to_string(0)

class DTSProperty:
    def __init__(self, parent, cls, field):
        self.parent = parent
        self.cls = cls
        self.field = field
        self.metadata = field.metadata["dts"]

        self.name = self.metadata.get_name()
        self.fieldtype = field.type
        self.subtype = self.metadata.type
        self.value = getattr(cls, field.name)


    def to_string(self, indent_level):
        if self.value is None:
            return ""

        if self.fieldtype == bool:
            if self.value in ("true", True):
                return indent("{};\n", indent_level).format(self.name)
        elif self.fieldtype == int:
            return indent("{} = <{}>;\n", indent_level).format(self.name, self.value)
        elif self.fieldtype == str:
            if self.subtype is None:
                return indent("{} = \"{}\";\n", indent_level).format(self.name, self.value)
        elif self.subtype == ESPHOME_PIN:
            soc = get_soc()
            port = soc.pin2dts.get_port(self.value)
            pin = soc.pin2dts.get_pin(self.value)
            flags = soc.pin2dts.get_flags(self.value)
            return indent("{} = <&{} {} {}>;\n", indent_level).format(self.name, port, pin, flags)
        elif self.subtype == ESPHOME_AUTOMATION:
            return indent("{} = \"{}\";\n", indent_level).format(self.name, do_generate_action_function_name(self.parent.name, self.cls, self.field))
        elif self.metadata.is_child():
            child_node = DTSNode(self.name, self.value)
            return child_node.to_string(indent_level)
        
        return None

class DTSCodeComponent(CodeComponentBase):
    def enabled(self):
        if self.obj.dts_compatible():
            return True
        return False

    @property
    def dts_compatible(self):
        return self.obj.dts_compatible()

class DTSBindingsCodeComponent(DTSCodeComponent):
    @property
    def dts_description(self):
        doc = self.obj.dts_description()
        if not doc:
            doc = "Bindings for {} ESPHome component".format(self.name)
        return doc

class DTSBindings(CodeGen):
    def __init__(self, out):
        super().__init__(out, DTSBindingsCodeComponent)
        self.bindings = {}
        self.indent_level = 0
        self.out = out

        self.current_binding = "default"
        self.bindings[self.current_binding] = ""

    def indent(self, indent_level, string):
        indent = ""
        for i in range(0, indent_level):
            indent += "  "
        return indent + string

    def get_type(self, component, field):
        dts_metadata = field.metadata["dts"]
        property = getattr(component, field.name)
        if field.type == bool:
            return "boolean"
        if field.type == int:
            return "int"
        if field.type == str:
            if dts_metadata.type == None:
                return "string"
            elif dts_metadata.type == ESPHOME_TIME:
                return "int"

        if dts_metadata.type == ESPHOME_PIN:
            return "phandle-array"
        if dts_metadata.type == ESPHOME_AUTOMATION:
            return "string"

        return None

    def get_enum(self, indent, component, field):
        bindings = ""
        dts_metadata = field.metadata["dts"]
        if dts_metadata.get_enum():
            bindings += self.indent(indent, "enum:\n")
            for enum in dts_metadata.get_enum():
                bindings += self.indent(indent+1, "- \"{}\"\n".format(enum))
        return bindings

    def property(self, component, field, indent):
        dts_metadata = field.metadata["dts"]
        bindings = self.indent(indent + 1, "{}:\n".format(dts_metadata.get_name()))
        bindings += self.indent(indent+ 2, "type: {}\n".format(self.get_type(component, field)))
        if dts_metadata.is_required():
            bindings += self.indent(indent+ 2, "required: true\n")
        else:
            bindings += self.indent(indent+ 2, "required: false\n")
            if field.default is not None:
                bindings += self.indent(indent + 2, "default: {}\n".format(str(field.default)))
        bindings += self.get_enum(indent + 2, component, field)
        if dts_metadata.get_doc():
            doc = dts_metadata.get_doc()
            bindings += self.indent(indent + 2, "description: |\n")
            for line in doc.split("\n"):
                if line.strip():
                    bindings += self.indent(indent + 3, "{}\n".format(line.strip()))
        return bindings

    def do_child_properties(self, component, child_bindings):
        bindings = self.indent(0, "child-binding:\n")
        bindings += child_bindings
        self.bindings[self.current_binding] += bindings

    def child_properties(self, component, indent=0):
        for field in fields(component.obj):
            if "dts" not in field.metadata:
                continue
            dts_metadata = field.metadata["dts"]
            if dts_metadata.is_child():
                # FIXME: Make CodeGen recursive
                bindings = DTSBindings(self.out)
                child = DTSBindingsCodeComponent(field.name, field.type)
                bindings.do_generate_static(child)
                if child.dts_compatible is None:
                    self.do_child_properties(component.obj, bindings.bindings["default"])

    def properties(self, component, indent=0,subfields=False):
        bindings = ""
        if subfields == False:
            bindings += self.indent(indent, "properties:\n")
        for field in fields(component.obj):
            if "dts" not in field.metadata:
                continue
            dts_metadata = field.metadata["dts"]
            if dts_metadata.is_field():
                # FIXME: Make CodeGen recursive
                bindings += self.property(component.obj, field, indent)
#            if "__dts_fields__" in field.metadata and field.metadata["__dts_fields__"]:
#                bindings += self.properties(field.type, indent,True)
        return bindings

    def compatible(self, component):
        if component.dts_compatible:
            self.bindings[self.current_binding] += "compatible: {}\n".format(component.dts_compatible)

    def description(self, component, indent=0):
        doc = component.dts_description
        if doc:
            self.bindings[self.current_binding] += self.indent(indent, "description: |\n")
            for line in doc.split("\n"):
                if line.strip():
                    self.bindings[self.current_binding] += self.indent(indent + 1, "{}\n".format(line.strip()))

    def do_init(self, component):
        if component is None:
            return
        if component.enabled():
            self.current_binding = component.dts_compatible
            self.bindings[self.current_binding] = ""

    def do_generate_static(self, component):
        if component is None:
            return

        if component.enabled():
            print("Generating dts bindings for {}".format(component.dts_compatible))
            self.compatible(component)
            self.description(component)
            self.bindings[self.current_binding] +=  self.properties(component)
            self.child_properties(component)
        else:
            print("Generating dts child bindings")
            self.description(component, 1)
            self.bindings[self.current_binding] +=  self.properties(component, 1)


    def do_write(self, component):
        if component is None or component.dts_compatible is None:
            return

        filename = component.dts_compatible + ".yaml"
        with open(self.out / filename, 'w') as dt_bindings:
            dt_bindings.write(self.bindings[component.dts_compatible])       

    def to_string(self, component):
        return self.bindings[self.current_binding]


class DTSCodeGen(CodeGen):
    def __init__(self, out):
        super().__init__(out, DTSCodeComponent)
        self.node = None
        self.current_componant_name = ""

    def do_init(self, component):
        if component is None and self.node is None:
            self.node = DTSRoot()

    def do_generate_runtime(self, component):
        if component is None:
            return

        if component.enabled():
            node = DTSNode(component.name, component.obj)
            self.node.add_child(node)

    def do_write(self, component):
        if component is not None:
            return

        esphome_dts_path = self.out / "esphome.overlay"
        with open(esphome_dts_path, 'w') as dts_file:
            dts_file.write(self.node.to_string())

    def to_string(self, component):
        return self.node.to_string()
