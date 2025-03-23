from dataclasses import fields
from codegen.codegen import CodeComponentBase, CodeGen

class PrjConfCodeComponent(CodeComponentBase):
    def enabled(self):
        if self.obj.kconfig_symbol():
            return True
        return False

    @property
    def symbol(self):
        return self.obj.kconfig_symbol()
    
    @property
    def dependencies(self):
        return self.obj.kconfig_dependencies()

class PrjConf(CodeGen):
    def __init__(self, out):
        super().__init__(out, PrjConfCodeComponent)
        self.symbols = {}

    def do_generate_runtime(self, component):
        if component is None:
            return

        if component.enabled():
            self.symbols[component.name] = []
            self.symbols[component.name] += component.dependencies
            self.symbols[component.name].append(component.symbol)

    def to_string(self, component=None):
        conf = ""
        for name, symbols in self.symbols.items():
            if component and component.name != name:
                continue
            conf += "# Enable {} component\n".format(name)
            for symbol in symbols:
                conf += "{}=y\n".format(symbol)
        return conf

    def do_write(self, component):
        if component is None:
            filename = self.out / "prj.conf"
            with open(filename, 'w') as prj_file:
                prj_file.write(self.to_string(None))

