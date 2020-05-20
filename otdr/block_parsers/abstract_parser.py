import logging
from abc import abstractmethod
from typing import BinaryIO

from otdr.base_parser import BaseParser
from otdr.block_data_structure import BaseBlockData

logger = logging.getLogger("pyOTDR")


class BlockParser(BaseParser):
    """
    Abstract class to create block parser (like MapBlock, GenParams, etc...)
    """

    data_class: BaseBlockData
    start_position: int = 0

    def __init__(self, filehandler: BinaryIO, start_position: int = 0):
        """
        start_position is the value where to seek to get the starting point of the data
        """
        super().__init__(filehandler)
        self.start_position = start_position

    @abstractmethod
    def parse(self):
        logger.debug(f"seeking at position {self.start_position}")
        self.filehandler.seek(self.start_position)
