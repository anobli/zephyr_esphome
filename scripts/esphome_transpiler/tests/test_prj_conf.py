from dataclasses import dataclass
import unittest

from yaml import safe_load

from codegen.prj_conf import PrjConf
from esphome_base import ESPHomeBase

test_yaml_1 = """
test:
    test1: 4
"""

test_prj_conf_1 = """\
# Enable test component
CONFIG_TEST_SYMBOL=y
"""

test_prj_conf_2 = """\
# Enable test component
CONFIG_TEST=y
CONFIG_TEST_SYMBOL=y
"""

class TestPrjConf(unittest.TestCase):
    def test_prj_conf(self):
        @dataclass
        class SubContainer(ESPHomeBase):
            test1: int = None
            test2: int = None

            @classmethod
            def kconfig_symbol(cls):
                return 'CONFIG_TEST_SYMBOL'

        @dataclass
        class Container(ESPHomeBase):
            test: SubContainer

        data = Container.from_dict(safe_load(test_yaml_1))
        conf = PrjConf(None)
        conf.generate(data)
        self.assertEqual(
            conf.to_string().strip(),
            test_prj_conf_1.strip()
        )

    def test_prj_conf_with_deps(self):
        @dataclass
        class SubContainer(ESPHomeBase):
            test1: int = None
            test2: int = None

            @classmethod
            def kconfig_symbol(cls):
                return 'CONFIG_TEST_SYMBOL'

            @classmethod
            def kconfig_dependencies(cls):
                return ['CONFIG_TEST']

        @dataclass
        class Container(ESPHomeBase):
            test: SubContainer

        data = Container.from_dict(safe_load(test_yaml_1))
        conf = PrjConf(None)
        conf.generate(data)
        self.assertEqual(
            conf.to_string().strip(),
            test_prj_conf_2.strip()
        )


if __name__ == '__main__':
    unittest.main()
