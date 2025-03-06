from esphome_base import ESPHomeBase, Automation, MixinField
from dataclasses import dataclass
from textwrap import dedent
from esphome_base import RequiredDTSField, DTSField
from esphome_const import ESPHOME_AUTOMATION

@dataclass
class ESPHomeProject(ESPHomeBase):
    name: str = RequiredDTSField()
    version: str = RequiredDTSField()
    on_update: list[Automation] = DTSField(type=ESPHOME_AUTOMATION)

@dataclass
class ESPHomeComponent(ESPHomeBase):
    name: str = MixinField(dts=True, cmake=True, required=True, name="entity_id", doc="""\
                This is the name of the node. It should always be unique in your ESPHome network.
                May only contain lowercase characters, digits and hyphens, and can be at most 24 characters
                long by default, or 31 characters long if name_add_mac_suffix is false.""")
    friendly_name: str = DTSField(doc="""\
                This is the name sent to the frontend.
                It is used by Home Assistant as the integration name, device name,
                and is automatically prefixed to entities where necessary.""")
    area: str = DTSField(doc="""\
                This is the area sent to the frontend.
                It is used by Home Assistant as the area / zone which the node belongs to.""")
    build_path: str = None
    platformio_options: str = None
    includes: str = None
    libraries: str = None
    comment: str = None
    name_add_mac_suffix: bool = DTSField(doc="""\
                Appends the last 3 bytes of the mac address of the device to the name
                in the form <name>-aabbcc.""")
    project: ESPHomeProject = None
    min_version: str = None
    compile_process_limit: int = None
    on_boot: list[Automation] = DTSField(doc="An automation to perform when the node starts.", type=ESPHOME_AUTOMATION)
    on_shutdown: list[Automation] = DTSField(doc="An automation to perform right before the node shuts down.", type=ESPHOME_AUTOMATION)
    on_loop: list[Automation] = DTSField(doc="An automation to perform on each loop() iteration.", type=ESPHOME_AUTOMATION)

    @classmethod
    def dts_compatible(cls):
        return "nabucasa,esphome"

    @classmethod
    def dts_description(cls):
        return dedent('''\
            Here you specify some core information that ESPHome needs to create firmwares.
            Most importantly, this is the section of the configuration where you specify
            the name of the node.''')

    @classmethod
    def kconfig_symbol(cls):
        return "CONFIG_ESPHOME"