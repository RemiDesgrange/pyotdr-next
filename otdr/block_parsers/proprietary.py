import logging

from otdr.block_data_structure import BaseBlockData
from otdr.block_parsers.abstract_parser import BlockParser

logger = logging.getLogger("pyOTDR")


class LnkParamsParser(BlockParser):
    def parse(self) -> BaseBlockData:
        super().parse()


class ProprietaryBlockParser(BlockParser):
    def parse(self) -> BaseBlockData:
        super().parse()
