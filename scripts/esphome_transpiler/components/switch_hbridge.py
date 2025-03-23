from dataclasses import dataclass
from dataclass_wizard import JSONWizard

from esphome_base import DTSField, RequiredDTSField
from esphome_const import ESPHOME_PIN, ESPHOME_TIME
from components.switch import Switch

@dataclass
class SwitchHbridge(Switch):
    class _(JSONWizard.Meta):
        tag = 'hbridge'
        tag_key = 'platform'

    on_pin: str = RequiredDTSField(name="on-gpios", type=ESPHOME_PIN)
    off_pin: str = RequiredDTSField(name="off-gpios", type=ESPHOME_PIN)
    pulse_length: str = DTSField(type=ESPHOME_TIME)
    wait_time: str = DTSField(type=ESPHOME_TIME)
    optimistic: bool = None

    @classmethod
    def dts_compatible(cls):
        return "nabucasa,esphome-switch-hbridge"

    @classmethod
    def dts_description(cls):
        return "The hbridge switch platform allows you to drive an h-bridge controlled latching relay."

    @classmethod
    def kconfig_symbol(cls):
        return "CONFIG_ESPHOME_COMPONENT_SWITCH_HBRIDGE"
    @classmethod
    def kconfig_dependencies(cls):
        return ["CONFIG_GPIO"]

        return ["CONFIG_GPIO"]
