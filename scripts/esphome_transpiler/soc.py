import glob
import importlib
from pathlib import Path


class PinData:
    """
    Represents data associated with a specific pin on a microcontroller.

    Attributes:
        port_name (str): The name of the GPIO port the pin belongs to (e.g., "GPIOA").
        pin (int): The pin number within the port (e.g., 0 for GPIOA_0).
    """
    def __init__(self, port_name, pin):
        self.port_name = port_name
        self.pin = pin


class Pin2Dts:
    """
    Manages the mapping between logical pin names and their associated data
    (port, pin number, flags) for Device Tree Source (DTS) generation.

    Attributes:
        pins (dict): A dictionary mapping logical pin names (e.g., "GPIO0")
                     to PinData objects.
    """
    def __init__(self):
        self.pins = {}

    def add_port(self, port_name, base, count):
        """
        Adds a range of pins belonging to a specific port.

        Args:
            port_name (str): The name of the GPIO port (e.g., "GPIOA").
            base (int): The starting pin number within the port.
            count (int): The number of pins in the range.
        """
        for pin in range(base, base + count):
            self.pins["GPIO{}".format(pin)] = PinData(port_name, pin - base)

    def get_port(self, pin):
        """
        Gets the port name associated with a given pin.

        Args:
            pin (Pin): a pin object.

        Returns:
            str: The name of the GPIO port.
        """
        return self.pins[pin.number].port_name

    def get_pin(self, pin):
        """
        Gets the pin number associated with a given pin.

        Args:
            pin (Pin): a pin object.

        Returns:
            int: The pin number within the port.
        """
        return self.pins[pin.number].pin

    def get_flags(self, pin):
        """
        Generates the DTS flags for a given pin based on its properties.

        Args:
            pin (Pin): The pin object for which to generate flags.

        Returns:
            str: A string representing the DTS flags (e.g., "(0 | GPIO_ACTIVE_LOW | GPIO_OPEN_DRAIN)").
        """
        flags = "(0"
        if pin.inverted:
            flags += " | GPIO_ACTIVE_LOW"
        if pin.mode:
            if pin.mode.open_drain:
                flags += " | GPIO_OPEN_DRAIN"
            if pin.mode.pullup:
                flags += " | GPIO_PULL_UP"
            if pin.mode.pulldown:
                flags += " | GPIO_PULL_DOWN"

        return flags + ")"


class SoC:
    """
    Base class for representing a System on Chip (SoC).

    Attributes:
        name (str): The name of the SoC (e.g., "cc1352p7").
        pin2dts (Pin2Dts): A Pin2Dts object managing the pins for this SoC.
    """
    def __init__(self, name):
        self.name = name
        self.pin2dts = Pin2Dts()


class SoCManager:
    """
    Manages the loading and selection of SoC (System on Chip) configurations.

    Attributes:
        _socs (dict): A dictionary mapping SoC names to SoC objects.
        current_soc (SoC): The currently selected SoC.
    """
    def __init__(self):
        """
        Initializes the SoCManager, loading available SoCs.
        """
        self._socs = {}
        self.load_socs()
        self.current_soc = None

    def load_socs(self):
        """
        Loads SoC configurations from Python modules in the 'socs' directory.

        Each Python module in the 'socs' directory is expected to define one or more
        subclasses of the SoC class.

        Raises:
            ImportError: If there is an error importing a module.
        """
        socs_path = Path(__file__).parent / "socs"
        if not socs_path.exists():
            print(f"Warning: Socs directory '{str(socs_path)}' not found.")
            return
        for module_path in socs_path.glob("*.py"):
            try:
                module_name = "socs." + module_path.stem
                module = importlib.import_module(module_name)
                for soc_cls in module.__dict__.values():
                    if isinstance(soc_cls, type) and issubclass(soc_cls, SoC) and soc_cls != SoC:
                        soc = soc_cls()
                        self._socs[soc.name] = soc
            except ImportError as e:
                print(f"Error importing SoC module {module_path}: {e}")

    def select_soc(self, name):
        """
        Selects a SoC by its name, making it the currently active SoC.

        Args:
            name (str): The name of the SoC to select.

        Raises:
            ValueError: If the specified SoC is not found.
        """
        soc = self._socs.get(name)
        if soc is None:
            raise ValueError(f"SoC '{name}' not found.")
        self.current_soc = soc

    def get_soc(self):
        """
        Gets the currently selected SoC.

        Returns:
            SoC: The currently selected SoC object.
            None: if no soc is selected.
        """
        return self.current_soc


soc_manager = SoCManager()


def select_soc(name):
    """
    Selects a SoC by name using the global SoCManager.

    Args:
        name (str): The name of the SoC to select.

    Returns:
        SoC: The selected SoC instance.
    """
    return soc_manager.select_soc(name)


def get_soc():
    """
    Gets the currently selected SoC from the global SoCManager.

    Returns:
        SoC: The currently selected SoC instance.
        None: if no soc is selected.
    """
    return soc_manager.get_soc()
