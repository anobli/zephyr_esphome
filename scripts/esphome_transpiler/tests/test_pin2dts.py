import unittest

from esphome_types.pin_schema import ESPHomePin
from soc import Pin2Dts

class TestPin2DTS(unittest.TestCase):
    def test_pin2dts_get_pin(self):
        pin2dts = Pin2Dts()
        pin2dts.add_port("gpio0", 0, 32)
        pin2dts.add_port("gpio1", 32, 16)

        gpio3 = ESPHomePin.from_dict({"number": "GPIO3"})
        port = pin2dts.get_port(gpio3)
        pin = pin2dts.get_pin(gpio3)
        self.assertEqual(port, "gpio0")
        self.assertEqual(pin, 3)

        gpio31 = ESPHomePin.from_dict({"number": "GPIO31"})
        port = pin2dts.get_port(gpio31)
        pin = pin2dts.get_pin(gpio31)
        self.assertEqual(port, "gpio0")
        self.assertEqual(pin, 31)

        gpio32 = ESPHomePin.from_dict({"number": "GPIO32"})
        port = pin2dts.get_port(gpio32)
        pin = pin2dts.get_pin(gpio32)
        self.assertEqual(port, "gpio1")
        self.assertEqual(pin, 0)

if __name__ == '__main__':
    unittest.main()
