from abc import ABC, abstractmethod
from typing import BinaryIO


class BaseParser(ABC):
    """
    Abstract class to create parser
    """

    filehandler: BinaryIO

    def __init__(self, filehandler: BinaryIO):
        self.filehandler = filehandler

    @abstractmethod
    def parse(self):
        pass
