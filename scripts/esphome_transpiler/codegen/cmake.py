from dataclasses import fields
from codegen.codegen import CodeComponentBase, CodeGen

class CMakeCodeComponent(CodeComponentBase):
    def enabled(self):
        return True

class CMake(CodeGen):
    def __init__(self, out):
        super().__init__(out, CMakeCodeComponent)
        self.variables = []
        self.project_name = ""

    def do_init(self, component):
        if component is None:
            self.load_tpl("CMakeLists.txt")


    def do_generate_runtime(self, component):
        if component is None:
            return

        for field in fields(component.obj):
            if "cmake" not in field.metadata:
                continue

            metadata = field.metadata["cmake"]
            if field.type == str:
                self.variables.append({
                    "name": metadata.get_name(),
                    "value": getattr(component.obj, field.name)
                })

    def do_substitute(self, component):
        if component is None:
            self.content = self.tpl.render(
                variables=self.variables,
                project_name=self.project_name
            )

    def do_write(self, component):
        if component is None:
            filename = self.out / "CMakeLists.txt"
            with open(filename, 'w') as cmake_file:
                cmake_file.write(self.content)

    def to_string(self, data):
        return self.content
