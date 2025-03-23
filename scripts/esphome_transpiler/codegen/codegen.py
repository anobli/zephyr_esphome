import abc
from dataclasses import fields
from jinja2 import Environment, PackageLoader

class CodeComponentBase:
    def __init__(self, name, obj):
        self.name = name
        self.obj = obj

    def defined(self):
        if self.obj is not None:
            return True
        return False

    def enabled(self):
        return False

class CodeGenBase:
    def __init__(self, out):
        self.content = ""
        self.tpl = None
        self.out = out
        self.env = Environment(loader=PackageLoader("apps"))

    def load_tpl(self, filename):
        self.tpl = self.env.get_template(filename)

    def do_init(self, component):
        pass

    def do_generate(self, component):
        pass

    def do_write(self, component):
        pass

    def write(self):
        self.out.mkdir(parents=True, exist_ok=True)
        for component in self.components:
            if not component.defined():
                continue
            self.do_write(component)
        self.do_write(None)

    def to_string(self, component=None):
        return ""

class CodeGen(CodeGenBase):
    def __init__(self, out, codegen_type):
        super().__init__(out)
        self.components = []
        self.type = codegen_type

    def init_static_components(self, cls):
        components = []
        for field in fields(cls):
            components.append(self.type(field.name, field.type))
        self.components = components

    def init_components(self, obj):
        components = []
        for field in fields(obj):
            component = getattr(obj, field.name)
            if isinstance(component, list):
                for component_element in component:
                    components.append(self.type(field.name, component_element))
            else:
                components.append(self.type(field.name, component))
        self.components = components

    def do_generate_runtime(self, component):
        pass

    def do_generate_static(self, component):
        pass

    def do_substitute(self, component):
        pass

    def generate(self, obj):
        if isinstance(obj, abc.ABCMeta):
            self.init_static_components(obj)
            generate_method = self.do_generate_static
        else:
            self.init_components(obj)
            generate_method = self.do_generate_runtime

        self.do_init(None)
        for component in self.components:
            if not component.defined():
                continue
            self.do_init(component)
            generate_method(component)
            if self.tpl:
                self.do_substitute(component)
        self.do_generate_static(None)
        if self.tpl:
            self.do_substitute(None)
