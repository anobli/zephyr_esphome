from dataclasses import fields
import hashlib
from pathlib import Path
from actions.action import get_automation_action_keys
from codegen.action_common import do_generate_action_content
from codegen.codegen import CodeComponentBase, CodeGen
from esphome_const import ESPHOME_AUTOMATION

class ActionCCodeComponent(CodeComponentBase):
    pass

class ActionC(CodeGen):
    def __init__(self, out):
        super().__init__(out, ActionCCodeComponent)

    def do_find_actions(self, component, field):
        components = []
        value = getattr(component, field.name)
        supported_actions = get_automation_action_keys()
        for curr_action in value.k_then:
            for action in supported_actions:
                if getattr(curr_action, action):
                    # This assumes that the first word is always the component name
                    # This might be false, we should find a better way for getting it
                    components.append(action.split("_")[0])
        return set(components)

    def do_generate_action(self, component_name, component, field):
        content = do_generate_action_content(component_name, component, field)
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        return "void esphome_{}_{}_{}(const struct device *dev)".format(
            component_name, field.name, content_hash) + content

    def do_generate_runtime(self, component):
        if component is None:
            return

        for field in fields(component.obj):
            if "dts" in field.metadata:
                metadata = field.metadata["dts"]
                # We should find a better for finding the type here
                if metadata.type == ESPHOME_AUTOMATION:
                    value = getattr(component.obj, field.name)
                    if value:
                        self.content += self.do_generate_action(component.name, component.obj, field)

    def to_string(self, component=None):
        return self.content

    def do_write(self, component):
        if component is None:
            with open(Path(__file__).parent.parent / "apps/templates/src/action.c", 'r') as base_file:
                c_path = self.out / "src/action.c"
                with open(c_path, 'w') as c_file:
                    c_file.write(base_file.read() + self.content)
