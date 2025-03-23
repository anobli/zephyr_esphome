"""Defines data classes for representing ESPHome pin configurations."""

from dataclasses import dataclass
from dataclass_wizard import JSONWizard


@dataclass
class PinSchemaMode(JSONWizard):
    """Represents the mode of a GPIO pin in ESPHome.

    Attributes:
        input (bool): True if the pin is configured as an input. Defaults to None.
        output (bool): True if the pin is configured as an output. Defaults to None.
        pullup (bool): True if a pull-up resistor is enabled. Defaults to None.
        pulldown (bool): True if a pull-down resistor is enabled. Defaults to None.
        open_drain (bool): True if open-drain mode is enabled. Defaults to None.
        analog (bool): True if the pin is configured as an analog input. Defaults to None.

    Raises:
        ValueError: If an unknown key is encountered in the JSON input.
    """
    input: bool = None
    output: bool = None
    pullup: bool = None
    pulldown: bool = None
    open_drain: bool = None
    analog: bool = None

    class _(JSONWizard.Meta):
        raise_on_unknown_json_key = True


@dataclass
class ESPHomePin(JSONWizard):
    """Represents a GPIO pin configuration in ESPHome.

    Attributes:
        number (str): The pin number or identifier (e.g., "GPIO1", "1").
        inverted (bool): True if the pin signal is inverted. Defaults to False.
        allow_other_uses (bool): If True, allows other peripherals to use the
            pin. Defaults to None.
        mode (PinSchemaMode): The pin's mode (input, output, etc.).
            Defaults to None.

    Raises:
        ValueError: If the pin number is invalid or if an unknown key is
            encountered in the JSON input.
        TypeError: if the mode is not a string or a dictionary.
    """
    number: str
    inverted: bool = False
    allow_other_uses: bool = None
    mode: PinSchemaMode = None

    class _(JSONWizard.Meta):
        raise_on_unknown_json_key = True

    @classmethod
    def _pre_from_dict(cls, o):
        """Preprocesses the dictionary before creating an ESPHomePin object.

        Handles string representations of modes and converts integer pin
        numbers to strings.

        Args:
            o (dict): The dictionary to process.

        Returns:
            dict: The processed dictionary.

        Raises:
            ValueError: If the input dictionary is invalid.
        """
        if "number" in o:
            if isinstance(o["number"], int):
                o["number"] = str(o["number"])
            elif isinstance(o["number"], str) and "GPIO" not in o["number"]:
                raise ValueError(f"Invalid pin number: {o['number']}")
        if "mode" in o:
            if isinstance(o["mode"], str):
                o["mode"] = cls._parse_mode_string(o["mode"])
            elif not isinstance(o["mode"], dict):
                raise TypeError(f"Invalid mode type: {type(o['mode'])}")
        return o

    @staticmethod
    def _parse_mode_string(mode_str: str) -> dict:
        """Parses a string representation of a pin mode into a dictionary.

        Args:
            mode_str (str): The string representation of the pin mode.

        Returns:
            dict: A dictionary representing the pin mode.

        Raises:
            ValueError: If the mode string is invalid.
        """
        mode = {}
        if mode_str == "INPUT":
            mode["input"] = True
        elif mode_str == "OUTPUT":
            mode["output"] = True
        elif mode_str == "ANALOG":
            mode["analog"] = True
        elif mode_str == "OUTPUT_OPEN_DRAIN":
            mode["output"] = True
            mode["open_drain"] = True
        elif mode_str == "INPUT_PULLUP":
            mode["input"] = True
            mode["pullup"] = True
        elif mode_str == "INPUT_PULLDOWN":
            mode["input"] = True
            mode["pulldown"] = True
        elif mode_str == "INPUT_OUTPUT_OPEN_DRAIN":
            mode["input"] = True
            mode["output"] = True
            mode["open_drain"] = True
        else:
            raise ValueError(f"Invalid mode string: {mode_str}")
        return mode
