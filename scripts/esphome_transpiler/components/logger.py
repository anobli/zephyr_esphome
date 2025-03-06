from textwrap import dedent
from dataclasses import dataclass
from esphome_base import ESPHomeBase, DTSField


@dataclass
class Logger(ESPHomeBase):
    baud_rate: int = DTSField(doc="The baud rate to use for the serial UART port. Defaults to 115200. Set to 0 to disable logging via UART.")
    level: str = DTSField(doc="The global log level. Any log message with a lower severity will not be shown. Defaults to DEBUG.")
    initial_level: str = DTSField(doc="The initial log level, which may be varied at run time. Defaults to the same value as level.")
    #logs (Optional, mapping): Manually set the log level for a specific component or tag. See Manual Log Levels for more information.
    #id (Optional, ID): Manually specify the ID used for code generation.

    @classmethod
    def dts_compatible(cls):
        return "nabucasa,esphome-logger"

    @classmethod
    def dts_description(cls):
        return dedent('''\
            The logger component automatically logs all log messages through the serial port
            and through MQTT topics (if there is an MQTT client in the configuration).
            By default, all logs with a severity DEBUG or higher will be shown.
            Increasing the log level severity (to e.g INFO or WARN) can help with the performance of
            the application and memory size.)''')

    @classmethod
    def kconfig_symbol(cls):
        return "CONFIG_ESPHOME_COMPONENT_LOGGER"
