from dataclasses import dataclass
from dataclass_wizard import JSONSerializable
from actions.action import AutomationActionBase, AutomationActionField, AutomationConditionField
from esphome_base import CRequiredField

@dataclass
class DoSomethingArgs(AutomationActionBase):
    class Meta(JSONSerializable.Meta):
        json_key_to_field = {
            'default_arg': 'sensor',
            '__all__': True
        }

    sensor: str = CRequiredField()
    arg1: str = None
    arg2: str = None


AutomationConditionField("test.is_off")
AutomationActionField("test.do_something", DoSomethingArgs)
AutomationActionField("test.do_something_else", DoSomethingArgs)
