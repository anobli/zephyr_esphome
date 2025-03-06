from dataclasses import dataclass
from esphome_base import CMakeField, ESPHomeBase

@dataclass
class Zephyr(ESPHomeBase):
    board: str = CMakeField(name="BOARD")
