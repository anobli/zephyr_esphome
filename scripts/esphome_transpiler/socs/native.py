from soc import SoC


class NativeSoC(SoC):
    """
    Represents a generic "native" System on Chip (SoC) for testing purposes.

    This class provides a minimal SoC definition primarily intended for use in
    unit tests and other situations where a simple, placeholder SoC is needed.
    It does not represent a specific real-world SoC architecture.

    Attributes:
        pin2dts (Pin2Dts): An instance of the Pin2Dts class managing pin mappings.
                           Initialized in the SoC base class.  Provides a basic
                           set of GPIO pins for testing.
    """
    def __init__(self):
        """
        Initializes the NativeSoC object with a default set of 32 GPIO pins.
        """
        super().__init__("native")
        self.pin2dts.add_port("gpio0", 0, 32)
