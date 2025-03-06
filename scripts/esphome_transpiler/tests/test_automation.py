from dataclasses import dataclass
from textwrap import dedent
import unittest

from dataclass_wizard import JSONWizard
from dataclass_wizard.errors import UnknownKeysError
from yaml import safe_load

from codegen.action_c import ActionC
from esphome_base import Automation, DTSField, ESPHomeBase
from esphome_const import ESPHOME_AUTOMATION

TEST_YAML_1 = """
test:
  on_test:
    then:
      - test.do_something: test_sensor
"""

TEST_YAML_2 = """
test:
  on_test:
    - then:
      - test.do_something: test_sensor
    - then:
      - test.do_something_else: test_sensor
"""

TEST_YAML_3 = """
test:
  on_test:
    then:
      - test.do_something:
          sensor: test_sensor
          arg1: val1
          arg2: val2
"""

TEST_YAML_4 = """
test:
  on_test:
    then:
      - if:
          condition:
            or:
              - test.is_off: test_sensor1
              - test.is_off: test_sensor2
          then:
              - test.do_something: test_sensor
"""

TEST_YAML_5 = """
test:
  on_test:
    then:
      - if:
          condition:
            or:
              - test.is_off: test_sensor1
              - test.is_off: test_sensor2
          else:
              - test.do_something_else: test_sensor
"""

TEST_YAML_6 = """
test:
  on_test:
    then:
      - if:
          condition:
            or:
              - test.is_off: test_sensor1
              - test.is_off: test_sensor2
          then:
              - test.do_something: test_sensor
          else:
              - test.do_something_else: test_sensor
"""

TEST_YAML_7 = """\
test:
  on_test:
  - test.do_something: test_sensor
  - test.do_something_else:
      test1: 5
      test2: 8
"""

TEST_YAML_8 = """\
test:
  on_test:
    then:
      - invalid.do_something: test_sensor
"""


@dataclass
class SubContainer(ESPHomeBase):
    class _(JSONWizard.Meta):
        recursive_classes = True
    on_test: list[Automation] = DTSField(type=ESPHOME_AUTOMATION)

@dataclass
class Container(ESPHomeBase):
    class _(JSONWizard.Meta):
        recursive_classes = True
    test: SubContainer


class TestAutomationAction(unittest.TestCase):
    def test_simple_action(self):
        test_yaml = dedent("""
        then:
          - test.do_something: test_sensor
        """)
        data = Automation.from_dict(safe_load(test_yaml))
        actions = data.k_then
        self.assertIsNotNone(actions[0].test_do_something)
        self.assertEqual(actions[0].test_do_something.sensor, "test_sensor")
        self.assertIsNone(actions[0].test_do_something_else)

    def test_two_actions(self):
        test_yaml = dedent("""
        then:
          - test.do_something: test_sensor
          - test.do_something_else: another_sensor
        """)
        data = Automation.from_dict(safe_load(test_yaml))
        actions = data.k_then
        self.assertIsNotNone(actions[0].test_do_something)
        self.assertEqual(actions[0].test_do_something.sensor, "test_sensor")
        self.assertIsNone(actions[0].test_do_something_else)

        self.assertIsNotNone(actions[1].test_do_something_else)
        self.assertEqual(actions[1].test_do_something_else.sensor, "another_sensor")
        self.assertIsNone(actions[1].test_do_something)

    def test_action_with_multiple_args(self):
        test_yaml = dedent("""
        then:
          - test.do_something:
              sensor: test_sensor
        """)
        data = Automation.from_dict(safe_load(test_yaml))
        actions = data.k_then
        self.assertIsNotNone(actions[0].test_do_something)
        self.assertEqual(actions[0].test_do_something.sensor, "test_sensor")
        self.assertIsNone(actions[0].test_do_something_else)

class TestAutomationParser(unittest.TestCase):
    def test_simple_automation(self):
        data = Container.from_dict(safe_load(TEST_YAML_1))
        action = data.test.on_test[0].k_then[0]
        self.assertIsNotNone(action.test_do_something)
        self.assertEqual(action.test_do_something.sensor, "test_sensor")

    def test_multiple_then(self):
        data = Container.from_dict(safe_load(TEST_YAML_2))

        actions = data.test.on_test[0].k_then
        self.assertIsNotNone(actions[0].test_do_something)
        self.assertEqual(actions[0].test_do_something.sensor, "test_sensor")
        self.assertIsNone(actions[0].test_do_something_else)

        actions = data.test.on_test[1].k_then
        self.assertIsNotNone(actions[0].test_do_something_else)
        self.assertEqual(actions[0].test_do_something_else.sensor, "test_sensor")
        self.assertIsNone(actions[0].test_do_something)


    def test_action_call_with_multiple_args(self):
        data = Container.from_dict(safe_load(TEST_YAML_3))
        action = data.test.on_test[0].k_then[0]

        self.assertIsNotNone(action.test_do_something)
        self.assertEqual(action.test_do_something.arg1, "val1")
        self.assertEqual(action.test_do_something.arg2, "val2")

    def test_action_if_cond_then(self):
        data = Container.from_dict(safe_load(TEST_YAML_4))

        cond = data.test.on_test[0].k_then[0].k_if.condition
        self.assertIsNotNone(cond.k_or)
        self.assertEqual(cond.k_or[0].test_is_off, "test_sensor1")
        self.assertEqual(cond.k_or[1].test_is_off, "test_sensor2")
        self.assertIsNone(cond.k_and)
        self.assertIsNone(cond.k_xor)

        actions = data.test.on_test[0].k_then[0].k_if.k_then
        self.assertIsNotNone(actions[0].test_do_something)
        self.assertEqual(actions[0].test_do_something.sensor, "test_sensor")

    def test_action_if_cond_else(self):
        data = Container.from_dict(safe_load(TEST_YAML_5))

        actions = data.test.on_test[0].k_then[0].k_if.k_else
        self.assertIsNotNone(actions[0].test_do_something_else)
        self.assertEqual(actions[0].test_do_something_else.sensor, "test_sensor")

    def test_action_if_cond_then_else(self):
        data = Container.from_dict(safe_load(TEST_YAML_6))

        actions = data.test.on_test[0].k_then[0].k_if.k_then
        self.assertIsNotNone(actions[0].test_do_something)
        self.assertEqual(actions[0].test_do_something.sensor, "test_sensor")

        actions = data.test.on_test[0].k_then[0].k_if.k_else
        self.assertIsNotNone(actions[0].test_do_something_else)
        self.assertEqual(actions[0].test_do_something_else.sensor, "test_sensor")

    def test_action_trigger_without_then(self):
        data = Container.from_dict(safe_load(TEST_YAML_7))


    def test_unknown_action(self):
        with self.assertRaises(UnknownKeysError):
            data = Container.from_dict(safe_load(TEST_YAML_8))


TEST_ACTION_C_1 = """\
void esphome_test_on_test_f8d1e8ae778051bb87ecd47afb773de5d85262da13ae3464eee9f62a8a6159d2(const struct device *dev){
	esphome_test_do_something("test_sensor",NULL,NULL);
}
"""

TEST_ACTION_C_2 = """\
void esphome_test_on_test_737d708ae7e65f46e289173e9eabb9a224bd4b24688c01dca6a6b4df8c83b576(const struct device *dev){
	esphome_test_do_something("test_sensor",NULL,NULL);
	esphome_test_do_something_else("test_sensor",NULL,NULL);
}
"""

TEST_ACTION_C_3 = """\
void esphome_test_on_test_ae848408ce67a921a75c7dc6773673a883e262cac2c0154aad105aa26ff83d2e(const struct device *dev){
	esphome_test_do_something("test_sensor","val1","val2");
}
"""

TEST_ACTION_C_4 = """\
void esphome_test_on_test_417121acb41bfc0553ad009ba2827ba0faa245e4e72ace88331bff1932d8471e(const struct device *dev){
	if(esphome_test_is_off(test_sensor1)||esphome_test_is_off(test_sensor2)){
		esphome_test_do_something("test_sensor",NULL,NULL);
	}
}
"""

TEST_ACTION_C_5 = """\
void esphome_test_on_test_d7c3cba965e8254b49b6b0ca8e53be8d74b0853e4da134cf37bafba778181872(const struct device *dev){
	if(esphome_test_is_off(test_sensor1)||esphome_test_is_off(test_sensor2)){
	} else {
		esphome_test_do_something_else("test_sensor",NULL,NULL);
	}
}
"""

TEST_ACTION_C_6 = """\
void esphome_test_on_test_eda56c348e7ea2f43e480f6b276b4d5f1a40415269a6b31437c7bf3f23c44b25(const struct device *dev){
	if(esphome_test_is_off(test_sensor1)||esphome_test_is_off(test_sensor2)){
		esphome_test_do_something("test_sensor",NULL,NULL);
	} else {
		esphome_test_do_something_else("test_sensor",NULL,NULL);
	}
}
"""

class TestActionC(unittest.TestCase):
    def test_simple_automation(self):
        data = Container.from_dict(safe_load(TEST_YAML_1))
        action_c = ActionC(None)
        action_c.generate(data)
        self.assertEqual(
            action_c.to_string(),
            TEST_ACTION_C_1
        )

    def test_multiple_then(self):
        data = Container.from_dict(safe_load(TEST_YAML_2))
        action_c = ActionC(None)
        action_c.generate(data)
        self.assertEqual(
            action_c.to_string(),
            TEST_ACTION_C_2
        )

    def test_action_call_with_multiple_args(self):
        data = Container.from_dict(safe_load(TEST_YAML_3))
        action_c = ActionC(None)
        action_c.generate(data)
        self.assertEqual(
            action_c.to_string(),
            TEST_ACTION_C_3
        )

    def test_action_if_cond_then(self):
        data = Container.from_dict(safe_load(TEST_YAML_4))
        action_c = ActionC(None)
        action_c.generate(data)
        self.assertEqual(
            action_c.to_string(),
            TEST_ACTION_C_4
        )

    def test_action_if_cond_else(self):
        data = Container.from_dict(safe_load(TEST_YAML_5))
        action_c = ActionC(None)
        action_c.generate(data)
        self.assertEqual(
            action_c.to_string(),
            TEST_ACTION_C_5
        )

    def test_action_if_cond_then_else(self):
        data = Container.from_dict(safe_load(TEST_YAML_6))
        action_c = ActionC(None)
        action_c.generate(data)
        self.assertEqual(
            action_c.to_string(),
            TEST_ACTION_C_6
        )


if __name__ == '__main__':
    unittest.main()
