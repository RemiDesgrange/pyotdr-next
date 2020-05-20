import logging

from otdr.block_data_structure import (
    GenParams,
    NmValue,
    FiberType,
)
from otdr.block_parsers.abstract_parser import BlockParser
from otdr.type_parser import (
    UShortParser,
    StringParser,
    IntParser,
)

logger = logging.getLogger("pyOTDR")


class GenParamsParserV1(BlockParser):
    def parse(self) -> GenParams:
        super().parse()
        fh = self.filehandler
        return GenParams(
            language=fh.read(2).decode("ascii"),
            cable_id=StringParser(fh).parse(),
            fiber_id=StringParser(fh).parse(),
            wavelength=NmValue(UShortParser(fh).parse()),
            locationA=StringParser(fh).parse(),
            locationB=StringParser(fh).parse(),
            cable_code=StringParser(fh).parse(),
            build_condition=fh.read(2).decode("ascii"),
            user_offset=IntParser(fh).parse(),
            operator=StringParser(fh).parse(),
            comment=StringParser(fh).parse(),
        )


class GenParamsParserV2(BlockParser):
    def parse(self) -> GenParams:
        super().parse()
        fh = self.filehandler
        # In V2 the block starts with the name of the block.
        block_name = fh.read(len("GenParams") + 1).decode("ascii")
        if block_name != "GenParams\0":
            raise ValueError(f"Block should be named GenParams but found {block_name}")
        return GenParams(
            language=fh.read(2).decode("ascii"),
            cable_id=StringParser(fh).parse(),
            fiber_id=StringParser(fh).parse(),
            fiber_type=FiberType(UShortParser(fh).parse()),
            wavelength=NmValue(UShortParser(fh).parse()),
            locationA=StringParser(fh).parse(),
            locationB=StringParser(fh).parse(),
            cable_code=StringParser(fh).parse(),
            build_condition=fh.read(2).decode("ascii"),
            user_offset=IntParser(fh).parse(),
            user_offset_distance=IntParser(fh).parse(),
            operator=StringParser(fh).parse(),
            comment=StringParser(fh).parse(),
        )
