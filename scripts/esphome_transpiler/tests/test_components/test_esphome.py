import unittest

from esphome_base import RequiredFieldError
from dataclass_wizard.errors import ParseError
from components.esphome import ESPHomeComponent

class TestESPHome(unittest.TestCase):
    def test_esphome(self):
        test_dict = {}
        with self.assertRaises(RequiredFieldError):
            data = ESPHomeComponent.from_dict(test_dict)
        
        test_dict = {"name": "test"}
        data = ESPHomeComponent.from_dict(test_dict)
        self.assertEqual(data.name, "test")

    def test_esphome_dts_simple(self):
        test_dict = {"name": "test"}
        data = ESPHomeComponent.from_dict(test_dict)
        dts_prop = data.get_dts_property("name")
        self.assertEqual("entity_id = \"test\";\n", dts_prop)

        test_dict = {
            "name": "test",
            "friendly_name": "A friendly name",
            "area": "A room",
            "name_add_mac_suffix": True,
        }
        data = ESPHomeComponent.from_dict(test_dict)
        dts_prop = data.get_dts_property("friendly_name")
        self.assertEqual("friendly_name = \"A friendly name\";\n", dts_prop)

    def test_esphome_dts_automation(self):
        pass

    def test_esphome_dts_project(self):
        pass

if __name__ == '__main__':
    unittest.main()
