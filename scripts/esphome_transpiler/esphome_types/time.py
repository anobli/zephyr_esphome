from dataclasses import dataclass
import re
from dataclass_wizard import JSONWizard

USEC = 1
USEC_PER_MSEC = 1000
USEC_PER_SEC = 1000000
USEC_PER_MIN = 60000000
USEC_PER_HOUR = 3600000000
USEC_PER_DAY = 86400000000

TIME_MULTIPLIERS = {
    'us': USEC,
    'ms': USEC_PER_MSEC,
    'milliseconds': USEC_PER_MSEC,
    's': USEC_PER_SEC,
    'seconds': USEC_PER_SEC,
    'min': USEC_PER_MIN,
    'minutes': USEC_PER_MIN,
    'h': USEC_PER_HOUR,
    'hours': USEC_PER_HOUR,
    'days': USEC_PER_DAY,
}
TIME_PATTERN1 = re.compile(r"(?P<value>\d+)(?P<unit>us|ms|s|min|h|days)")
TIME_PATTERN2 = re.compile(r"(?P<hour>\d+):(?P<min>\d+)(:(?P<sec>\d+))?")


def is_valid_hour(value):
    """Checks if a value is a valid hour (0-23).

    Args:
        value: The hour value to check.

    Returns:
        bool: True if the value is a valid hour, False otherwise.
    """
    if value < 0 or value > 23:
        return False
    return True


def is_valid_min(value):
    """Checks if a value is a valid minute (0-59).

    Args:
        value: The minute value to check.

    Returns:
        bool: True if the value is a valid minute, False otherwise.
    """
    if value < 0 or value > 59:
        return False
    return True


def is_valid_sec(value):
    """Checks if a value is a valid second (0-59).

    Args:
        value: The second value to check.

    Returns:
        bool: True if the value is a valid second, False otherwise.
    """
    if value < 0 or value > 59:
        return False
    return True


def is_valid_time(value, unit):
    """Checks if a time value is valid for a given unit.

    Args:
        value: The time value to check.
        unit: The time unit (e.g., USEC_PER_HOUR).

    Returns:
        bool: True if the value is valid for the given unit, False otherwise.
    """
    if unit == USEC_PER_HOUR:
        return is_valid_hour(value)
    if unit == USEC_PER_MIN:
        return is_valid_min(value)
    if unit == USEC_PER_SEC:
        return is_valid_sec(value)
    return True


def parse_string_value(value):
    """Parses a time string in the format <value><unit> (e.g., 10s, 500ms).

    Args:
        value: The time string to parse.

    Returns:
        int: The time in microseconds, or None if the string is not in the correct format.
    """
    match = TIME_PATTERN1.fullmatch(value)
    if match:
        value = int(match.group("value"))
        unit = TIME_MULTIPLIERS[match.group("unit")]
        if not is_valid_time(value, unit):
            raise ValueError(value)
        return value * unit
    return None


def parse_formated_value(value):
    """Parses a time string in HH:MM:SS format.

    Args:
        value: The time string to parse.

    Returns:
        int: The time in microseconds, or None if the string is not in the correct format.
    """
    match = TIME_PATTERN2.fullmatch(value)
    if match:
        hour = int(match.group("hour"))
        if not is_valid_hour(hour):
            raise ValueError(value)
        min = int(match.group("min"))
        if not is_valid_min(min):
            raise ValueError(value)
        sec = 0
        if match.group("sec"):
            sec = int(match.group("sec"))
        if not is_valid_sec(sec):
            raise ValueError(value)
        total_sec = hour * 3600 + min * 60 + sec
        return total_sec * 1000000
    return None


def parse_special_value(value):
    """Parses special time values ("always" and "never").

    Args:
        value: The time string to parse.

    Returns:
        int: 0 for "always", -1 for "never", or None if the string is not a special value.
    """
    if value == "always":
        return 0
    if value == "never":
        return -1

    return None


def parse_dict(value):
    """Parses a dictionary specifying time components.

    Args:
        value: The dictionary to parse.

    Returns:
        int: The time in microseconds.

    Raises:
        ValueError: If the dictionary contains invalid time units or values.
    """
    yaml = value
    us = 0
    for unit in yaml:
        if unit in TIME_MULTIPLIERS:
            if not is_valid_time(yaml[unit], TIME_MULTIPLIERS[unit]):
                raise ValueError(value)
            us += yaml[unit] * TIME_MULTIPLIERS[unit]
        else:
            raise ValueError(value)
    return us


def parse_time(value):
    """Parses a time specification from various formats.

    Args:
        value: The time specification. Can be a string (numeric with unit, HH:MM:SS, "always", "never") or a dictionary.

    Returns:
        int: The time in microseconds.

    Raises:
        ValueError: If the time specification is invalid.
        TypeError: If the time specification has an unsupported type.
    """
    if isinstance(value, str):
        if parse_string_value(value) is not None:
            return parse_string_value(value)

        if parse_formated_value(value) is not None:
            return parse_formated_value(value)

        if parse_special_value(value) is not None:
            return parse_special_value(value)

        raise ValueError(value)

    if isinstance(value, dict):
        return parse_dict(value)

    raise TypeError(value)


@dataclass
class ESPHomeTime(JSONWizard):
    """Represents a time specification in microseconds.

    Attributes:
        us (int): The time in microseconds.
    """
    us: int

    @classmethod
    def _pre_from_dict(cls, o):
        """Pre-processes the dictionary before creating an ESPHomeTime object.

        Args:
            o: The dictionary to process.

        Returns:
            dict: A dictionary containing the time in microseconds.

        Raises:
            ValueError: If the time specification is invalid.
        """
        return {"us": parse_time(o)}
