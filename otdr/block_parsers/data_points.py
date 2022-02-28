import logging

from otdr.block_data_structure import DataPoints
from otdr.block_parsers.abstract_parser import BlockParser
from otdr.type_parser import ShortParser, UintParser, UShortParser

logger = logging.getLogger("pyOTDR")


class DataPtsParserV1(BlockParser):
    def parse(self) -> DataPoints:
        super().parse()
        fh = self.filehandler
        number_of_points = UintParser(fh).parse()
        logger.debug(f"{number_of_points=} in DataPts")
        num_trace = ShortParser(fh).parse()
        if num_trace > 1:
            logger.error(
                "Cannot handle sor file with multiple trace. Just 1 will be processed."
            )
        _ = UintParser(fh).parse()  # number of point again
        scaling_factor = UShortParser(fh).parse() / 1000.0
        points = [UShortParser(fh).parse() for _ in range(number_of_points)]
        fs = 0.001 * scaling_factor
        return DataPoints(
            min(points) * fs,
            max(points) * fs,
            number_of_points,
            num_trace,
            scaling_factor,
            points,
        )


class DataPtsParserV2(BlockParser):
    def parse(self) -> DataPoints:
        super().parse()
        fh = self.filehandler
        block_name = fh.read(len("DataPts") + 1).decode("ascii")
        if block_name != "DataPts\0":
            raise ValueError(f"Block name should be DataPts got {block_name}")
        number_of_points = UintParser(fh).parse()
        logger.debug(f"{number_of_points=} in DataPts")
        num_trace = ShortParser(fh).parse()
        if num_trace > 1:
            logger.error(
                "Cannot handle sor file with multiple trace. Just 1 will be processed."
            )
        _ = UintParser(fh).parse()  # number of point again
        scaling_factor = UShortParser(fh).parse() / 1000.0
        points = [UShortParser(fh).parse() for _ in range(number_of_points)]
        fs = 0.001 * scaling_factor
        return DataPoints(
            min(points) * fs,
            max(points) * fs,
            number_of_points,
            num_trace,
            scaling_factor,
            points,
        )
