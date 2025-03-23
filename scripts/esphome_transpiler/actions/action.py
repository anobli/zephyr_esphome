from dataclasses import fields
from pathlib import Path
from dataclass_wizard import JSONWizard, json_field

import importlib
import glob


automation_actions = []
automation_conditions = []
automation_hdr = {}

def import_actions():
    for module in glob.glob("actions/*.py", root_dir=Path(__file__).parent.parent):
        mod = importlib.import_module(module.replace('/', '.')[0:-3])

def get_automation_actions():
    import_actions()
    actions = [
        ('k_if', 'AutomationIf', json_field('if', default=None, all=True))
    ]
    return actions + automation_actions

def get_automation_conditions():
    return automation_conditions

def get_automation_action_keys():
    keys = []
    for action in automation_actions:
        keys.append(action[0])
    return keys

def get_automation_condition_keys():
    keys = []
    for action in automation_conditions:
        keys.append(action[0])
    return keys


def AutomationActionField(action, type, default=None):
    key = action.replace(".", "_")
    field = (key, type, json_field(action, default=default, all=True))
    automation_actions.append(field)

def AutomationConditionField(condition):
    key = condition.replace(".", "_")
    field = (key, str, json_field(condition, all=True, metadata={"condition": True}))
    automation_conditions.append(field)

def AutomationActionDependency(component, header_name=None, path=None):
    if path is None:
        path = Path("esphome/component")
    if header_name is None:
        header_name = component + ".h"
    automation_hdr[component] = path / header_name

# Same definition as in esphome_base
# This is to avoid circular dependencies
class RequiredFieldError(Exception):
    def __init__(self, name):
        super().__init__("{} field is not defined".format(name))

class UnsupportedTypeError(Exception):
    def __init__(self, name):
        super().__init__("{} field type is not supported".format(name))

class UnsupportedActionError(Exception):
    def __init__(self, name):
        super().__init__("{} is not a valid action".format(name))

class AutomationActionBase(JSONWizard):
    @classmethod
    def is_none(cls, key, o):
        if key not in o or o[key] is None:
            return True
        return False

    @classmethod
    def _pre_from_dict(cls, o):
        # Check that mandatory args are defined
        for field in fields(cls):
            if "dts" in field.metadata:
                dts_metadata = field.metadata["dts"]
                if dts_metadata.required:
                    if cls.is_none(field.name, o):
                        raise RequiredFieldError("name")

        if isinstance(o, dict):
            return o

        # Sometime, we may expect a dict but passing a single argument
        # is accepted. Convert this single value to a dict.
        return {"default_arg": o}
