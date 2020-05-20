import logging

import crcmod

from otdr.block_data_structure import Cksum
from otdr.block_parsers.abstract_parser import BlockParser
from otdr.type_parser import UShortParser

logger = logging.getLogger("pyOTDR")


class CksumParserV1(BlockParser):
    def parse(self) -> Cksum:
        super().parse()
        fh = self.filehandler
        file_cs = UShortParser(fh).parse()
        fh.seek(0)
        computed_cs = crcmod.predefined.Crc("crc-ccitt-false")
        computed_cs.update(fh.read(self.start_position))
        return Cksum(file_cs, computed_cs.crcValue, file_cs == computed_cs.crcValue)


class CksumParserV2(BlockParser):
    def parse(self) -> Cksum:
        super().parse()
        fh = self.filehandler
        block_name = fh.read(len("Cksum") + 1).decode("ascii")
        if block_name != "Cksum\0":
            raise ValueError(f"Block name should be Cksum got {block_name}")
        file_cs = UShortParser(fh).parse()
        fh.seek(0)
        computed_cs = crcmod.predefined.Crc("crc-ccitt-false")
        computed_cs.update(fh.read(self.start_position+len('Cksum\0')))
        return Cksum(file_cs, computed_cs.crcValue, file_cs == computed_cs.crcValue)
