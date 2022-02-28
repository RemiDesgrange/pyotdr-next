import logging
import struct

from otdr.base_parser import BaseParser

logger = logging.getLogger("pyOTDR")

# Abstract class to create Type parser (like Uint, Int, Float, Short etc...)
TypeParser = BaseParser


class StringParser(TypeParser):
    """
    In SOR file, string is ended when `\00` is present.
    """

    def parse(self) -> str:
        result = b""
        byte = self.filehandler.read(1)
        while byte != "":
            tt = struct.unpack("c", byte)[0]
            if tt == b"\x00":
                break
            result += tt
            byte = self.filehandler.read(1)

        return result.decode("utf-8")


class UintParser(TypeParser):
    """
    Parse base unisgned int.
    """

    def parse(self) -> int:
        return struct.unpack("<I", self.filehandler.read(4))[0]


class UShortParser(TypeParser):
    def parse(self) -> int:
        return struct.unpack("<H", self.filehandler.read(2))[0]


class ULongParser(TypeParser):
    def parse(self) -> int:
        return struct.unpack("<Q", self.filehandler.read(8))[0]


class IntParser(TypeParser):
    def parse(self) -> int:
        return struct.unpack("<i", self.filehandler.read(4))[0]


class ShortParser(TypeParser):
    def parse(self) -> int:
        return struct.unpack("<h", self.filehandler.read(2))[0]


class LongParser(TypeParser):
    def parse(self) -> int:
        return struct.unpack("<q", self.filehandler.read(8))[0]


class FloatParser(TypeParser):
    def parse(self) -> float:
        return struct.unpack("<f", self.filehandler.read(4))[0]


class DoubleParser(TypeParser):
    def parse(self) -> float:
        return struct.unpack("<d", self.filehandler.read(8))[0]
