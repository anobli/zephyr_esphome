import unittest

from components.zephyr import Zephyr

class TestZephyrCMake(unittest.TestCase):
    def test_zephyr_cmake(self):
        data = Zephyr.from_dict({"board": "Test"})
        self.assertEqual(data.board, "Test")

if __name__ == '__main__':
    unittest.main()
