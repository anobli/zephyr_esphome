import unittest
from dataclass_wizard.errors import UnknownKeysError, MissingFields
from esphome_types.pin_schema import ESPHomePin, PinSchemaMode


class TestESPHomePin(unittest.TestCase):
    def test_esphomepin_from_dict_basic(self):
        pin = ESPHomePin.from_dict({"number": "GPIO1"})
        self.assertEqual(pin.number, "GPIO1")
        self.assertFalse(pin.inverted)
        self.assertIsNone(pin.allow_other_uses)
        self.assertIsNone(pin.mode)

    def test_esphomepin_from_dict_inverted(self):
        pin = ESPHomePin.from_dict({"number": "GPIO1", "inverted": True})
        self.assertEqual(pin.number, "GPIO1")
        self.assertTrue(pin.inverted)
        self.assertIsNone(pin.allow_other_uses)
        self.assertIsNone(pin.mode)

    def test_esphomepin_from_dict_allow_other_uses(self):
        pin = ESPHomePin.from_dict({"number": "GPIO1", "allow_other_uses": True})
        self.assertEqual(pin.number, "GPIO1")
        self.assertFalse(pin.inverted)
        self.assertTrue(pin.allow_other_uses)
        self.assertIsNone(pin.mode)

    def test_esphomepin_from_dict_mode(self):
        pin = ESPHomePin.from_dict({"number": "GPIO1", "mode": "INPUT"})
        self.assertEqual(pin.number, "GPIO1")
        self.assertFalse(pin.inverted)
        self.assertIsNone(pin.allow_other_uses)
        self.assertEqual(pin.mode, PinSchemaMode(input=True))

    def test_esphomepin_from_dict_mode_complex(self):
        pin = ESPHomePin.from_dict({"number": "GPIO1", "mode": "INPUT_PULLUP"})
        self.assertEqual(pin.number, "GPIO1")
        self.assertFalse(pin.inverted)
        self.assertIsNone(pin.allow_other_uses)
        self.assertEqual(pin.mode, PinSchemaMode(input=True, pullup=True))

    def test_esphomepin_from_dict_mode_dict(self):
        pin = ESPHomePin.from_dict({"number": "GPIO1", "mode": {"input": True}})
        self.assertEqual(pin.number, "GPIO1")
        self.assertFalse(pin.inverted)
        self.assertIsNone(pin.allow_other_uses)
        self.assertEqual(pin.mode, PinSchemaMode(input=True))

    def test_esphomepin_from_dict_int_number(self):
        pin = ESPHomePin.from_dict({"number": 1})
        self.assertEqual(pin.number, "1")

    def test_esphomepin_schema_mode_from_dict(self):
        mode = PinSchemaMode.from_dict({"input": True})
        self.assertEqual(mode, PinSchemaMode(input=True))

    def test_esphomepin_schema_mode_from_dict_complex(self):
        mode = PinSchemaMode.from_dict({"input": True, "pullup": True, "open_drain": True})
        self.assertEqual(mode, PinSchemaMode(input=True, pullup=True, open_drain=True))

    def test_esphomepin_schema_mode_from_dict_invalid(self):
        with self.assertRaises(UnknownKeysError):
            PinSchemaMode.from_dict({"invalid": True})

    def test_esphomepin_from_dict_invalid_number(self):
        with self.assertRaises(ValueError):
            ESPHomePin.from_dict({"number": "invalid"})

    def test_esphomepin_from_dict_invalid_mode(self):
        with self.assertRaises(ValueError):
            ESPHomePin.from_dict({"number": "GPIO1", "mode": "invalid"})

    def test_esphomepin_from_dict_missing_number(self):
        with self.assertRaises(MissingFields):
            ESPHomePin.from_dict({})


if __name__ == "__main__":
    unittest.main()
