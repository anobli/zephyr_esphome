from dataclasses import dataclass
from esphome_base import ESPHomeBase, DTSField, DTSEnumField
from esphome_const import ESPHOME_AUTOMATION

@dataclass
class Switch(ESPHomeBase):
   platform: str
   id: str = DTSField()
   name: str = DTSField(name="device_name")
   icon: str = None
   inverted: bool = DTSField()
   internal: bool = DTSField()
   restore_mode: str = DTSEnumField([
      "RESTORE_DEFAULT_OFF",
      "RESTORE_DEFAULT_ON",
      "RESTORE_INVERTED_DEFAULT_OFF",
      "RESTORE_INVERTED_DEFAULT_ON",
      "ALWAYS_OFF",
      "ALWAYS_ON",
      "DISABLED",
    ], default="ALWAYS_OFF")
   on_turn_on: str = DTSField(type=ESPHOME_AUTOMATION)
   on_turn_off: str = DTSField(type=ESPHOME_AUTOMATION)
   disabled_by_default: bool = None
   entity_category: str = None
   device_class: str = None
