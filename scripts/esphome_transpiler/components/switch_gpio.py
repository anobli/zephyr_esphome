from textwrap import dedent
from dataclass_wizard import JSONWizard
from dataclasses import dataclass

from esphome_base import RequiredDTSField
from esphome_const import ESPHOME_PIN
from components.switch import Switch

@dataclass
class SwitchGpio(Switch):
    class _(JSONWizard.Meta):
        tag = 'gpio'
        tag_key = 'platform'

    pin: str = RequiredDTSField(name="gpios", type=ESPHOME_PIN)

    @classmethod
    def dts_compatible(cls):
        return "nabucasa,esphome-switch-gpio"

    @classmethod
    def dts_description(cls):
        return dedent('''\'
            The switch domain includes all platforms that should show up like a switch
            and can only be turned ON or OFF''')

    @classmethod
    def kconfig_symbol(cls):
        return "CONFIG_ESPHOME_COMPONENT_SWITCH_GPIO"

    @classmethod
    def kconfig_dependencies(cls):
        return ["CONFIG_GPIO"]
