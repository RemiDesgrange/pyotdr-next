import logging
from abc import abstractmethod
from typing import Type, List, BinaryIO

from otdr.base_parser import BaseParser
from otdr.block_data_structure import BaseBlockData, Block, MapBlock
from otdr.type_parser import UintParser, UShortParser, StringParser

logger = logging.getLogger("pyOTDR")


class BlockParser(BaseParser):
    """
    Abstract class to create block parser (like MapBlock, GenParams, etc...)
    """

    data_class: BaseBlockData

    def __init__(self, filehandler: BinaryIO, start_position: int = 0):
        """
        start_position is the value where to seek to get the starting point of the data
        """
        super().__init__(filehandler)
        logger.debug(f"seeking at position {start_position}")
        self.filehandler.seek(start_position)

    @abstractmethod
    def parse(self) -> BaseBlockData:
        pass


class MapBlockParser(BlockParser):
    def parse(self) -> MapBlock:
        fh = self.filehandler
        version = UShortParser(fh).parse() * 0.01
        nbytes = UintParser(fh).parse()
        # get number of block; not including the Map block
        number_of_block = UShortParser(fh).parse() - 1
        block_position = nbytes
        blocks = list()
        for i in range(number_of_block):
            bname = StringParser(fh).parse()
            bversion = UShortParser(fh).parse() * 0.01
            bsize = UintParser(fh).parse()
            block = Block(bname, i, block_position, bsize, f"{bversion:.2f}")
            blocks.append(block)
            block_position += bsize
        return MapBlock(blocks, version, nbytes)


class GenParamsParser(BlockParser):
    def parse(self) -> BaseBlockData:
        pass


class SupParamsParser(BlockParser):
    def parse(self) -> BaseBlockData:
        pass


class FxdParamsParser(BlockParser):
    def parse(self) -> BaseBlockData:
        pass


class KeyEventsParser(BlockParser):
    def parse(self) -> BaseBlockData:
        pass


class LnkParamsParser(BlockParser):
    def parse(self) -> BaseBlockData:
        pass


class DataPtsParser(BlockParser):
    def parse(self) -> BaseBlockData:
        pass


class ProprietaryBlockParser(BlockParser):
    def parse(self) -> BaseBlockData:
        pass


class CksumParser(BlockParser):
    def parse(self) -> BaseBlockData:
        pass
