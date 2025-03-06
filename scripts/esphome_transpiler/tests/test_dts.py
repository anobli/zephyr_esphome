from dataclasses import dataclass
from pathlib import Path
import sys
import tempfile

from esphome_types.pin_schema import ESPHomePin
from codegen.dts import DTSCodeGen, DTSBindings, DTSNode, DTSRoot
from esphome_const import ESPHOME_AUTOMATION
from esphome_base import ESPHomeBase, Automation, DTSField, DTSChildField, RequiredGpioDTSField
from soc import select_soc
sys.path.append("../")

import unittest
from yaml import safe_load

test_yaml_1 = """
test:
    test1: 4
"""

test_dts_1 = """
/{
	test{
		compatible="test,test";
		test1 = <4>;
	};
};
"""

test_bindings_1 = """
compatible: test,test
description: |
  Bindings for test ESPHome component
properties:
  test1:
    type: int
    required: false
  test2:
    type: int
    required: false
"""

test_yaml_2 = """
test:
    test1: true
    test2: false
"""

test_dts_2 = """
/{
	test{
		compatible="test,test";
		test1;
	};
};
"""

test_bindings_2 = """
compatible: test,test
description: |
  Bindings for test ESPHome component
properties:
  test1:
    type: boolean
    required: false
  test2:
    type: boolean
    required: false
"""

test_yaml_3 = """
test:
    test1: true
    test2: false
    test3:
        test4: 3
        test5: 6
"""

test_dts_3 = """
/{
	test{
		compatible="test,test";
		test1;
		test3{
			test4 = <3>;
			test5 = <6>;
		};
	};
};
"""

test_bindings_3 = """
compatible: test,test
description: |
  Bindings for test ESPHome component
properties:
  test1:
    type: boolean
    required: false
  test2:
    type: boolean
    required: false
child-binding:
  description: |
    Bindings for test3 ESPHome component
  properties:
    test4:
      type: int
      required: false
    test5:
      type: int
      required: false
"""

test_yaml_4 = """
test:
  on_test:
  - test.do_something: test_sensor
"""

test_dts_4 = """
/{
	test{
		compatible="test,test";
		on_test = "esphome_test_on_test_f8d1e8ae778051bb87ecd47afb773de5d85262da13ae3464eee9f62a8a6159d2";
	};
};
"""

test_yaml_5 = """
test:
  on_test:
  - test.do_something: test_sensor
  - test.do_something_else:
      test1: 5
      test2: 8
"""

test_dts_5 = """
/{
	test{
		compatible="test,test";
		on_test = "esphome_test_on_test_85c5e372075798211efae44fc01c99bb92f1102fdaf57961da10097fe47661b4";
	};
};
"""

TEST_YAML_6 = """
test:
  gpio1: GPIO12
  gpio2:
      number: GPIO14
"""

TEST_BINDINGS_6 = """
compatible: test,test
description: |
  Bindings for test ESPHome component
properties:
  pin1-gpios:
    type: phandle-array
    required: true
  pin2-gpios:
    type: phandle-array
    required: true
"""

TEST_YAML_7 = """
test:
  - pin: GPIO12
  - pin: 13
  - pin:
      number: GPIO14
      inverted: true
  - pin:
      number: GPIO15
      mode:
        input: true
        pullup: true
  - pin:
      number: GPIO16
      mode: OUTPUT_OPEN_DRAIN
"""

TEST_DTS_7 = """
/{
	test{
		compatible="test,test";
		pin-gpios = <&gpio0 12 (0)>;
	};
	test{
		compatible="test,test";
		pin-gpios = <&gpio0 13 (0)>;
	};
	test{
		compatible="test,test";
		pin-gpios = <&gpio0 14 (0 | GPIO_ACTIVE_LOW)>;
	};
	test{
		compatible="test,test";
		pin-gpios = <&gpio0 15 (0 | GPIO_PULL_UP)>;
	};
	test{
		compatible="test,test";
		pin-gpios = <&gpio0 16 (0 | GPIO_OPEN_DRAIN)>;
	};
};
"""

TEST_YAML_8 = """
switch:
  - platform: gpio
    pin: GPIOXX
    name: "Relay #1"
    id: relay1

  - platform: gpio
    pin:
      number: GPIO14
      inverted: true
    name: "Relay #2"
    id: relay2

  - platform: gpio
    pin: 15
    name: "Relay #3"
    id: relay3
"""


class TestDTSRoot(unittest.TestCase):
    def test_dts_root_empty(self):
        node = DTSRoot()
        self.assertEqual(node.to_string(), "/{\n};\n")

    def test_dts_root_with_child(self):
        @dataclass
        class SubContainer(ESPHomeBase):
            test1: int = DTSField()
            test2: int = DTSField()

            @classmethod
            def dts_compatible(cls):
                return 'test,test'


        @dataclass
        class Container(ESPHomeBase):
            test: SubContainer

        data = Container.from_dict(safe_load(test_yaml_1))
        node = DTSRoot()
        child_node = DTSNode("test", data.test)
        node.add_child(child_node)
        self.assertEqual(
            node.to_string().strip(),
            test_dts_1.strip()
        )


class TestDTS(unittest.TestCase):
    def test_dts(self):
        @dataclass
        class SubContainer(ESPHomeBase):
            test1: int = DTSField()
            test2: int = DTSField()

            @classmethod
            def dts_compatible(cls):
                return 'test,test'

        @dataclass
        class Container(ESPHomeBase):
            test: SubContainer

        data = Container.from_dict(safe_load(test_yaml_1))
        dts = DTSCodeGen(None)
        dts.generate(data)
        self.assertEqual(
            dts.to_string(data).strip(),
            test_dts_1.strip()
        )

    def test_dts_property_bool(self):
        @dataclass
        class SubContainer(ESPHomeBase):
            test1: bool = DTSField()
            test2: bool = DTSField()

            @classmethod
            def dts_compatible(cls):
                return 'test,test'

        @dataclass
        class Container(ESPHomeBase):
            test: SubContainer

        data = Container.from_dict(safe_load(test_yaml_2))
        dts = DTSCodeGen(None)
        dts.generate(data)
        self.assertEqual(
            dts.to_string(data).strip(),
            test_dts_2.strip()
        )

    def test_dts_property_write(self):
        @dataclass
        class SubContainer(ESPHomeBase):
            test1: bool = DTSField()
            test2: bool = DTSField()

            @classmethod
            def dts_compatible(cls):
                return 'test,test'

        @dataclass
        class Container(ESPHomeBase):
            test: SubContainer

        data = Container.from_dict(safe_load(test_yaml_2))
        with tempfile.TemporaryDirectory() as tmpdirname:
            out = Path(tmpdirname)
            dts = DTSCodeGen(out)
            dts.generate(data)
            dts.write()

            with open(out / "esphome.overlay", 'r') as esphome_overlay:
                self.assertEqual(
                    esphome_overlay.read().strip(),
                    test_dts_2.strip()
            )

    def test_dts_child(self):
        @dataclass
        class SubContainer2(ESPHomeBase):
            test4: int = DTSField()
            test5: int = DTSField()

        @dataclass
        class SubContainer(ESPHomeBase):
            test1: bool = DTSField()
            test2: bool = DTSField()
            test3: SubContainer2 = DTSChildField()

            @classmethod
            def dts_compatible(cls):
                return 'test,test'

        @dataclass
        class Container(ESPHomeBase):
            test: SubContainer

        data = Container.from_dict(safe_load(test_yaml_3))

        dts = DTSCodeGen(None)
        dts.generate(data)
        self.assertEqual(
            dts.to_string(data).strip(),
            test_dts_3.strip()
        )

    def test_dts_automation(self):
        @dataclass
        class SubContainer(ESPHomeBase):
            on_test: list[Automation] = DTSField(type=ESPHOME_AUTOMATION)

            @classmethod
            def dts_compatible(cls):
                return 'test,test'

        @dataclass
        class Container(ESPHomeBase):
            test: SubContainer
        print(safe_load(test_yaml_4))
        data = Container.from_dict(safe_load(test_yaml_4))

        dts = DTSCodeGen(None)
        dts.generate(data)
        self.assertEqual(
            dts.to_string(data).strip(),
            test_dts_4.strip()
        )

        data = Container.from_dict(safe_load(test_yaml_5))

        dts = DTSCodeGen(None)
        dts.generate(data)
        self.assertEqual(
            dts.to_string(data).strip(),
            test_dts_5.strip()
        )
    
    def test_dts_gpio(self):
        @dataclass
        class SubContainer(ESPHomeBase):
            pin: ESPHomePin = RequiredGpioDTSField(name="pin-gpios")

            @classmethod
            def dts_compatible(cls):
                return 'test,test'

        @dataclass
        class Container(ESPHomeBase):
            test: list[SubContainer]

        data = Container.from_dict(safe_load(TEST_YAML_7))
        select_soc("native")

        dts = DTSCodeGen(None)
        dts.generate(data)
        self.assertEqual(
            dts.to_string(data).strip(),
            TEST_DTS_7.strip()
        )

    def test_dts_without_dts_field(self):
        @dataclass
        class SubContainer(ESPHomeBase):
            test1: int = DTSField()
            test2: int = None

            @classmethod
            def dts_compatible(cls):
                return 'test,test'

        @dataclass
        class Container(ESPHomeBase):
            test: SubContainer

        data = Container.from_dict(safe_load(test_yaml_1))
        dts = DTSCodeGen(None)
        dts.generate(data)
        self.assertEqual(
            dts.to_string(data).strip(),
            test_dts_1.strip()
        )


class TestDTSBindings(unittest.TestCase):
    def test_dts_bindings(self):
        @dataclass
        class SubContainer(ESPHomeBase):
            test1: int = DTSField()
            test2: int = DTSField()

            @classmethod
            def dts_compatible(cls):
                return 'test,test'

        @dataclass
        class Container(ESPHomeBase):
            test: SubContainer

        dts = DTSBindings(None)
        dts.generate(Container)
        self.assertEqual(
            dts.to_string(Container).strip(),
            test_bindings_1.strip()
        )

    def test_dts_bindings_bool(self):
        @dataclass
        class SubContainer(ESPHomeBase):
            test1: bool = DTSField()
            test2: bool = DTSField()

            @classmethod
            def dts_compatible(cls):
                return 'test,test'

        @dataclass
        class Container(ESPHomeBase):
            test: SubContainer

        dts = DTSBindings(None)
        dts.generate(Container)
        self.assertEqual(
            dts.to_string(Container).strip(),
            test_bindings_2.strip()
        )

    def test_dts_bindings_child(self):
        @dataclass
        class ChildContainer(ESPHomeBase):
            test4: int = DTSField()
            test5: int = DTSField()

        @dataclass
        class SubContainer(ESPHomeBase):
            test1: bool = DTSField()
            test2: bool = DTSField()
            test3: ChildContainer = DTSChildField()

            @classmethod
            def dts_compatible(cls):
                return 'test,test'

        @dataclass
        class Container(ESPHomeBase):
            test: SubContainer

        dts = DTSBindings(None)
        dts.generate(Container)
        self.assertEqual(
            dts.to_string(Container).strip(),
            test_bindings_3.strip()
        )

    def test_dts_bindings_gpio(self):
        @dataclass
        class SubContainer(ESPHomeBase):
            gpio1: ESPHomePin = RequiredGpioDTSField(name="pin1-gpios")
            gpio2: ESPHomePin = RequiredGpioDTSField(name="pin2-gpios")

            @classmethod
            def dts_compatible(cls):
                return 'test,test'

        @dataclass
        class Container(ESPHomeBase):
            test: SubContainer

        dts = DTSBindings(None)
        dts.generate(Container)
        self.assertEqual(
            dts.to_string(Container).strip(),
            TEST_BINDINGS_6.strip()
        )


if __name__ == '__main__':
    unittest.main()
