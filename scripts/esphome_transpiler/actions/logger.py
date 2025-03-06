from dataclasses import dataclass

from dataclass_wizard import JSONSerializable
from actions.action import AutomationActionBase, AutomationActionField, AutomationActionDependency
from esphome_base import CRequiredField, CVargsField

@dataclass
class LoggerActionLog(AutomationActionBase):
    class Meta(JSONSerializable.Meta):
        json_key_to_field = {
            'default_arg': 'format',
            '__all__': True
        }

    level: str = "DEBUG"
    tag: str = "main"
    format: str = CRequiredField()
    args: list = CVargsField()

AutomationActionDependency("logger")
AutomationActionField("logger.log", LoggerActionLog)
