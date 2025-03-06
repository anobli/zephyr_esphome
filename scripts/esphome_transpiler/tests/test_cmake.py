from dataclasses import dataclass
import sys

from codegen.cmake import CMake
from esphome_base import CMakeField, ESPHomeBase
sys.path.append("../")

import unittest
from yaml import safe_load

TEST_YAML_1 = """
test:
  test1: value
  test2: another value
"""

TEST_CMAKE_1 = """
# SPDX-License-Identifier: Apache-2.0

cmake_minimum_required(VERSION 3.20.0)

# Set variables
set(DTC_OVERLAY_FILE esphome.overlay)

set(test1 value)

set(TEST2 another value)


find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(esphome_)

target_sources(app
    PRIVATE
        src/main.c
        src/action.c
)
"""

class TestCMake(unittest.TestCase):
    def test_cmake(self):
        @dataclass
        class SubContainer(ESPHomeBase):
            test1: str = CMakeField()
            test2: str = CMakeField(name="TEST2")

        @dataclass
        class Container(ESPHomeBase):
            test: SubContainer

        data = Container.from_dict(safe_load(TEST_YAML_1))
        cmake = CMake(None)
        cmake.generate(data)
        self.assertEqual(cmake.to_string(data), TEST_CMAKE_1.strip())


if __name__ == '__main__':
    unittest.main()
