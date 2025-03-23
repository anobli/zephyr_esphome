from soc import SoC


class CC1352P7(SoC):
    """
    Represents the Texas Instruments CC1352P7 System on Chip (SoC).

    This class provides SoC-specific information for the CC1352P7, including
    pin mappings and other relevant data used in Device Tree Source (DTS)
    generation.

    Attributes:
        pin2dts (Pin2Dts): An instance of the Pin2Dts class managing pin
        mappings for this SoC.  Initialized in the SoC base class.
    """
    def __init__(self):
        """
        Initializes the CC1352P7 SoC object, setting up its pin mappings.
        """
        super().__init__("cc1352p7")
        self.pin2dts.add_port("gpio0", 0, 32)
