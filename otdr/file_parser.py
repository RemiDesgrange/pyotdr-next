import logging
from abc import ABC
from io import IOBase
from pathlib import Path
from typing import BinaryIO, Type, Union, List

from otdr.block_data_structure import Block, BaseBlockData, MapBlock
from otdr.block_parser import (
    MapBlockParser,
    BlockParser,
    CksumParser,
    DataPtsParser,
    SupParamsParserV1,
    SupParamsParserV2,
    FxdParamsParser,
    KeyEventsParserV1,
    KeyEventsParserV2,
    LnkParamsParser,
    ProprietaryBlockParser, GenParamsParserV2, GenParamsParserV1,
)
from otdr.type_parser import StringParser

logger = logging.getLogger("pyOTDR")


class ParserFactory:
    """return a SorParserV1 or V2"""

    @staticmethod
    def create_parser(sor_file: Union[BinaryIO, Path]) -> "BaseSorParser":
        """
        Create a parser based on the
        """
        if isinstance(sor_file, Path):
            filehandle = open(sor_file, "rb")
        else:
            filehandle = sor_file

        return VersionParser(filehandle).parse()


class BaseSorParser(ABC):
    version: int = 0
    filename: str
    filehandle: BinaryIO
    part_parser: "PartParser"
    map_block: MapBlock

    def __init__(self, sor_file: Union[BinaryIO, Path]):
        if isinstance(sor_file, Path):
            self.filehandle = open(sor_file, "rb")
        elif isinstance(sor_file, IOBase):
            self.filehandle = sor_file
        else:
            raise TypeError(
                f"Argument sor_file should be a filename or a file object. Got {type(sor_file)}"
            )
        self.part_parser = PartParser()


    def parse(self) -> List[BaseBlockData]:
        parsed = self.part_parser.parse()
        parsed.append(self.map_block)
        return parsed


class PartParser:
    """
    Pass all parser to this class and return parsed data.
    """

    parsers: List[BlockParser]

    def __init__(self):
        self.parsers = list()

    def register_parser(self, parser: BlockParser):
        self.parsers.append(parser)

    def parse(self) -> List[BaseBlockData]:
        return [p.parse() for p in self.parsers]


class SorParserV1(BaseSorParser):
    version: int = 1

    def __init__(self, sor_file: Union[BinaryIO, Path]):
        super().__init__(sor_file)
        self.map_block = MapBlockParser(self.filehandle).parse()
        for block in self.map_block.blocks:
            parser = self._find_parser_for_block(block)
            # if a parser exists for this
            if parser:
                self.part_parser.register_parser(parser)

    def _find_parser_for_block(self, block: Block) -> BlockParser:
        blocks = {
            "Cksum": CksumParser,
            "DataPts": DataPtsParser,
            "GenParams": GenParamsParserV1,
            "SupParams": SupParamsParserV1,
            "FxdParams": FxdParamsParser,
            "KeyEvents": KeyEventsParserV1,
            "LnkParams": LnkParamsParser,
            "ProprietaryBlock": ProprietaryBlockParser,
        }
        for name, parser_class in blocks.items():
            if block.name == name:
                return parser_class(self.filehandle, block.position)

class SorParserV2(BaseSorParser):
    version: int = 2
    map_block: MapBlock

    def __init__(self, sor_file: Union[BinaryIO, Path]):
        super().__init__(sor_file)
        self.map_block = MapBlockParser(self.filehandle, 4).parse()
        for block in self.map_block.blocks:
            parser = self._find_parser_for_block(block)
            # if a parser exists for this
            if parser:
                self.part_parser.register_parser(parser)

    def _find_parser_for_block(self, block: Block) -> BlockParser:
        blocks = {
            "Cksum": CksumParser,
            "DataPts": DataPtsParser,
            "GenParams": GenParamsParserV2,
            "SupParams": SupParamsParserV2,
            "FxdParams": FxdParamsParser,
            "KeyEvents": KeyEventsParserV2,
            "LnkParams": LnkParamsParser,
            "ProprietaryBlock": ProprietaryBlockParser,
        }
        for name, parser_class in blocks.items():
            if block.name == name:
                return parser_class(self.filehandle, block.position)

class VersionParser:
    """
    Parse the version based on the first bytes of the sor file. If the file
    starts with a "Map" string then the format is v2, else it's v1.
    """

    filehandle: BinaryIO

    def __init__(self, fh: BinaryIO) -> None:
        self.filehandle = fh
        fh.seek(0)

    def parse(self) -> BaseSorParser:
        res = StringParser(self.filehandle).parse()
        self.filehandle.seek(0)  # ensure we are returning at the begining of the file
        if res == "Map":
            return SorParserV2(self.filehandle)
        else:
            return SorParserV1(self.filehandle)
