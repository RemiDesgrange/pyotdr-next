from abc import ABC, abstractmethod
from typing import BinaryIO, List


class BaseParser(ABC):
    """
    Abstract class to create parser
    """

    filehandler: BinaryIO
    speed_of_light: float = 299792.458 / 1.0e6  # = 0.299792458 km/usec

    def __init__(self, filehandler: BinaryIO):
        self.filehandler = filehandler

    @abstractmethod
    def parse(self):
        pass
