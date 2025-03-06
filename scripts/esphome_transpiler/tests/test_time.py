from dataclasses import dataclass
import unittest

from dataclass_wizard import JSONWizard
from esphome_types.time import (
    ESPHomeTime,
    parse_time,
    TIME_MULTIPLIERS,
    TIME_PATTERN1,
    TIME_PATTERN2,
)

@dataclass
class Container(JSONWizard):
    delay: ESPHomeTime

class TestTime(unittest.TestCase):
    def test_parse_time_numeric(self):
        self.assertEqual(parse_time("10us"), 10)
        self.assertEqual(parse_time("10ms"), 10000)
        self.assertEqual(parse_time("10s"), 10000000)
        self.assertEqual(parse_time("10min"), 600000000)
        self.assertEqual(parse_time("10h"), 36000000000)
        self.assertEqual(parse_time("10days"), 864000000000)
        with self.assertRaises(ValueError):
            parse_time("10x")

    def test_parse_time_hms(self):
        self.assertEqual(parse_time("10:00:00"), 36000000000)
        self.assertEqual(parse_time("10:00"), 36000000000)
        self.assertEqual(parse_time("00:10:00"), 600000000)
        self.assertEqual(parse_time("00:00:10"), 10000000)
        with self.assertRaises(ValueError):
            parse_time("10:60:00")
        with self.assertRaises(ValueError):
            parse_time("10:00:60")
        with self.assertRaises(ValueError):
            parse_time("10:00:00:00")

    def test_parse_time_dict(self):
        self.assertEqual(parse_time({"seconds": 10}), 10000000)
        self.assertEqual(parse_time({"milliseconds": 10}), 10000)
        self.assertEqual(parse_time({"minutes": 10, "seconds": 5}), 605000000)
        with self.assertRaises(ValueError):
            parse_time({"x": 10})

    def test_parse_time_special_cases(self):
        self.assertEqual(parse_time("always"), 0)
        self.assertEqual(parse_time("never"), -1)

    def test_parse_time_invalid(self):
        with self.assertRaises(ValueError):
            parse_time("invalid")
        with self.assertRaises(TypeError):
            parse_time(123)

    def test_esphome_time_from_dict(self):
        self.assertEqual(Container.from_dict({"delay": "10s"}).delay.us, 10000000)
        self.assertEqual(Container.from_dict({"delay": "10:00"}).delay.us, 36000000000)
        self.assertEqual(Container.from_dict({"delay": {"seconds": 10}}).delay.us, 10000000)
        with self.assertRaises(ValueError):
            ESPHomeTime.from_dict({"delay": "invalid"})

    def test_esphome_time_from_dict_invalid(self):
        with self.assertRaises(ValueError):
            ESPHomeTime.from_dict({"delay_us": "invalid"})

    def test_time_multipliers(self):
        self.assertEqual(TIME_MULTIPLIERS["us"], 1)
        self.assertEqual(TIME_MULTIPLIERS["ms"], 1000)
        self.assertEqual(TIME_MULTIPLIERS["s"], 1000000)
        self.assertEqual(TIME_MULTIPLIERS["min"], 60000000)
        self.assertEqual(TIME_MULTIPLIERS["h"], 3600000000)
        self.assertEqual(TIME_MULTIPLIERS["days"], 86400000000)

    def test_time_patterns(self):
        self.assertTrue(TIME_PATTERN1.fullmatch("10us"))
        self.assertTrue(TIME_PATTERN1.fullmatch("10ms"))
        self.assertTrue(TIME_PATTERN2.fullmatch("10:00"))
        self.assertTrue(TIME_PATTERN2.fullmatch("10:00:00"))
        self.assertFalse(TIME_PATTERN1.fullmatch("10:00"))
        self.assertFalse(TIME_PATTERN2.fullmatch("10us"))

if __name__ == "__main__":
    unittest.main()
