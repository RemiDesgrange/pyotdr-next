from otdr.block_data_structure import BaseBlockData
from otdr.block_parsers.abstract_parser import BlockParser


class FxdParamsParserV1(BlockParser):
    def parse(self) -> BaseBlockData:
        super().parse()


class FxdParamsParserV2(BlockParser):
    def parse(self) -> BaseBlockData:
        super().parse()
