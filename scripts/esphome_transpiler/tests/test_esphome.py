from pathlib import Path
import unittest
from esphome import ESPHome, get_project_path

class TestESPHome(unittest.TestCase):
    def test_esphome(self):
        data = ESPHome.from_dict({
            "esphome": {"name": "test"},
            "zephyr": {"board": "native_posix"},
        })
        self.assertEqual(data.esphome.name, "test")
        self.assertEqual(data.zephyr.board, "native_posix")

    def test_esphome_log_hello(self):
        data = ESPHome.from_dict({
            'logger': {},
            'esphome': {
                'name': 'HelloWorld',
                'on_boot':
                    {'then': [{'logger.log': 'Hello World'}]}
            },
            'zephyr': {'board': 'native_posix'},
        })
        self.assertEqual(data.esphome.name, "HelloWorld")
        self.assertEqual(data.zephyr.board, "native_posix")
        self.assertEqual(data.esphome.on_boot[0].k_then[0].logger_log.format, "Hello World")

    def test_esphome_get_project_path(self):
        test_dir = Path(__file__).parent
        project_path = get_project_path(test_dir / "yaml/esphome-helloworld.yaml", test_dir / "test_out")
        self.assertEqual(project_path, test_dir / "test_out/esphome_HelloWorld")

if __name__ == '__main__':
    unittest.main()
