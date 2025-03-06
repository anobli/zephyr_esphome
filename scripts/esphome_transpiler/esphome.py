from dataclasses import dataclass
from pathlib import Path
from shutil import copy
from typing import List, Optional

from yaml import safe_load
from dataclass_wizard import JSONWizard

from codegen.action_c import ActionC
from codegen.cmake import CMake
from codegen.dts import DTSBindings, DTSCodeGen
from codegen.prj_conf import PrjConf
from components.zephyr import Zephyr
from components.esphome import ESPHomeComponent
from components.logger import Logger
from components.switch_gpio import SwitchGpio
from components.switch_hbridge import SwitchHbridge

from esphome_base import dts_components

@dataclass
class ESPHome(JSONWizard):
    class _(JSONWizard.Meta):
        tag_key = 'platform'
        auto_assign_tags = True
        recursive_classes = True

    esphome: ESPHomeComponent
    zephyr: Zephyr
    logger: Optional[Logger] = None
    switch: List[SwitchGpio | SwitchHbridge] = None

def get_project_path(yaml_file, path):
    project_path = None
    with open(yaml_file) as file:
        data = ESPHome.from_dict(safe_load(file.read()))
        project_path  = path / "esphome_{}".format(data.esphome.name)
    return project_path

def generate_dts_bindings(path):
    dtb = DTSBindings(path)
    dtb.generate(dts_components)
    dtb.write(dts_components)

def generate_dts(yaml_file, path):
    with open(yaml_file) as file:
        data = ESPHome.from_dict(safe_load(file.read()))
        dts = DTSCodeGen(path)
        dts.generate(data)
        dts.write()

def generate_cmake(yaml_file, path):
    with open(yaml_file) as file:
        data = ESPHome.from_dict(safe_load(file.read()))
        cmake = CMake(path)
        cmake.generate(data)
        cmake.write()

def generate_action(yaml_file, path):
    with open(yaml_file) as file:
        data = ESPHome.from_dict(safe_load(file.read()))
        c = ActionC(path)
        c.generate(data)
        c.write()

def generate_prj_conf(yaml_file, path):
    with open(yaml_file) as file:
        data = ESPHome.from_dict(safe_load(file.read()))
        conf = PrjConf(path)
        conf.generate(data)
        conf.write()


#        c = ActionHdr(self.out_path / "src")
#        c.generate(self.components)
#        c.write(self.components)

def generate_app(yaml_file, path):
    src_path = path / "src"
    path.mkdir(parents=True, exist_ok=True)
    src_path.mkdir(parents=True, exist_ok=True)

    generate_dts(yaml_file, path)
    generate_cmake(yaml_file, path)
    generate_action(yaml_file, path)
    generate_prj_conf(yaml_file, path)
    copy(Path(__file__).parent / "apps/templates/src/main.c", src_path / "main.c")

