import logging

from otdr.block_data_structure import (
    Block,
    MapBlock,
)
from otdr.block_parsers.abstract_parser import BlockParser
from otdr.type_parser import (
    UintParser,
    UShortParser,
    StringParser,
)

logger = logging.getLogger("pyOTDR")


class MapBlockParser(BlockParser):
    def parse(self) -> MapBlock:
        super().parse()
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
