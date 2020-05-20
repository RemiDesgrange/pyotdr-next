import logging

from otdr.block_data_structure import SupParams
from otdr.block_parsers.abstract_parser import BlockParser
from otdr.type_parser import StringParser

logger = logging.getLogger("pyOTDR")


class SupParamsParserV1(BlockParser):
    def parse(self) -> SupParams:
        super().parse()
        fh = self.filehandler
        return SupParams(
            supplier=StringParser(fh).parse(),
            OTDR=StringParser(fh).parse(),
            OTDR_serial_number=StringParser(fh).parse(),
            module=StringParser(fh).parse(),
            module_serial_number=StringParser(fh).parse(),
            software=StringParser(fh).parse(),
            other=StringParser(fh).parse(),
        )


class SupParamsParserV2(BlockParser):
    def parse(self) -> SupParams:
        super().parse()
        fh = self.filehandler
        block_name = fh.read(len("SupParams") + 1).decode("ascii")
        if block_name != "SupParams\0":
            raise ValueError(f"Block name should be SupParams got {block_name}")
        return SupParams(
            supplier=StringParser(fh).parse(),
            OTDR=StringParser(fh).parse(),
            OTDR_serial_number=StringParser(fh).parse(),
            module=StringParser(fh).parse(),
            module_serial_number=StringParser(fh).parse(),
            software=StringParser(fh).parse(),
            other=StringParser(fh).parse(),
        )
