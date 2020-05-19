import logging
import re
from abc import abstractmethod
from typing import BinaryIO


from otdr.base_parser import BaseParser
from otdr.block_data_structure import BaseBlockData, Block, MapBlock, GenParams, NmValue, FiberType, SupParams, \
    KeyEvents, Event, EventDataType, EventType, EventModeType, KeyEventSummary
from otdr.type_parser import UintParser, UShortParser, StringParser, IntParser

logger = logging.getLogger("pyOTDR")


class BlockParser(BaseParser):
    """
    Abstract class to create block parser (like MapBlock, GenParams, etc...)
    """

    data_class: BaseBlockData
    start_position: int = 0

    def __init__(self, filehandler: BinaryIO, start_position: int = 0):
        """
        start_position is the value where to seek to get the starting point of the data
        """
        super().__init__(filehandler)
        self.start_position = start_position

    @abstractmethod
    def parse(self):
        logger.debug(f"seeking at position {self.start_position}")
        self.filehandler.seek(self.start_position)


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


class GenParamsParserV1(BlockParser):
    def parse(self) -> GenParams:
        super().parse()
        fh = self.filehandler
        return GenParams(
            language=fh.read(2).decode('ascii'),
            cable_id=StringParser(fh).parse(),
            fiber_id=StringParser(fh).parse(),
            wavelength=NmValue(UShortParser(fh).parse()),
            locationA=StringParser(fh).parse(),
            locationB=StringParser(fh).parse(),
            cable_code=StringParser(fh).parse(),
            build_condition=fh.read(2).decode('ascii'),
            user_offset=IntParser(fh).parse(),
            operator=StringParser(fh).parse(),
            comment=StringParser(fh).parse()
        )

class GenParamsParserV2(BlockParser):
    def parse(self) -> GenParams:
        super().parse()
        fh = self.filehandler
        # In V2 the block starts with the name of the block.
        block_name = fh.read(len('GenParams')+1).decode('ascii')
        if block_name != "GenParams\0":
            raise ValueError(f"Block should be named GenParams but found {block_name}")
        return GenParams(
            language=fh.read(2).decode('ascii'),
            cable_id=StringParser(fh).parse(),
            fiber_id=StringParser(fh).parse(),
            fiber_type=FiberType(UShortParser(fh).parse()),
            wavelength=NmValue(UShortParser(fh).parse()),
            locationA=StringParser(fh).parse(),
            locationB=StringParser(fh).parse(),
            cable_code=StringParser(fh).parse(),
            build_condition=fh.read(2).decode('ascii'),
            user_offset=IntParser(fh).parse(),
            user_offset_distance=IntParser(fh).parse(),
            operator=StringParser(fh).parse(),
            comment=StringParser(fh).parse()
        )



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
            other=StringParser(fh).parse()
        )

class SupParamsParserV2(BlockParser):
    def parse(self) -> SupParams:
        super().parse()
        fh = self.filehandler
        block_name = fh.read(len('SupParams')+1).decode('ascii')
        if block_name != 'SupParams\0':
            raise ValueError(f'Block name should be SupParams got {block_name}')
        return SupParams(
            supplier=StringParser(fh).parse(),
            OTDR=StringParser(fh).parse(),
            OTDR_serial_number=StringParser(fh).parse(),
            module=StringParser(fh).parse(),
            module_serial_number=StringParser(fh).parse(),
            software=StringParser(fh).parse(),
            other=StringParser(fh).parse()
        )

class FxdParamsParser(BlockParser):
    def parse(self) -> BaseBlockData:
        super().parse()


class KeyEventsParserV1(BlockParser):
    def parse(self) -> KeyEvents:
        super().parse()
        fh = self.filehandler
        number_of_events = UShortParser(fh).parse()
        logger.debug(f"{number_of_events=}")
        events = list()
        for e in range(number_of_events):
            events.append(self._parse_events())
        summary = self._parse_summary()
        return KeyEvents(summary, events)

    def _parse_events(self) -> Event:
        fh = self.filehandler
        factor = 1 #TODO factor is in FxdParams. How to get it ?
        _ = UShortParser(fh).parse() # event number
        distance = UintParser(fh).parse()
        slope = UShortParser(fh).parse() * 0.001
        splice_loss = UShortParser(fh).parse() * 0.001
        refl_loss = UintParser(fh).parse() * 0.001
        evt_raw_type = fh.read(8).decode('ascii')
        evt_type = self._parse_event_type(evt_raw_type)
        return Event(
            distance=distance,
            slope=slope,
            splice_loss=splice_loss,
            refl_loss=refl_loss,
            type=evt_type,
            comment = StringParser(fh).parse(),
        )

    def _parse_event_type(self, evt_type: str) -> EventDataType:
        evt_type_pattern = re.compile("(.)(.)9999LS")
        match_res = evt_type_pattern.match(evt_type)
        if match_res is not None:
            subtype = match_res.groups(0)[0]
            mode = match_res.groups(0)[1]
            return EventDataType(evt_type, EventType(int(subtype)), EventModeType(mode))
        else:
            return EventDataType(evt_type, EventType.unknown, EventModeType.unknown)

    def _parse_summary(self) -> KeyEventSummary:
        factor = 1 #TODO factor is in FxdParams. How to get it ?
        return KeyEventSummary(
            total_loss=IntParser(self.filehandler).parse()*0.001,
            loss_start=IntParser(self.filehandler).parse()*factor,
            loss_end=UintParser(self.filehandler).parse()*factor,
            ORL=UShortParser(self.filehandler).parse()*0.001,
            ORL_start=IntParser(self.filehandler).parse()*factor,
            ORL_finish=UintParser(self.filehandler).parse()*factor
        )


class KeyEventsParserV2(BlockParser):
    def parse(self) -> KeyEvents:
        super().parse()
        fh = self.filehandler
        block_name = fh.read(len('KeyEvents')+1).decode('ascii')
        if block_name != 'KeyEvents\0':
            raise ValueError(f'Block name should be KeyEvents got {block_name}')
        number_of_events = UShortParser(fh).parse()
        logger.debug(f"{number_of_events=}")
        events = list()
        for e in range(number_of_events):
            events.append(self._parse_events())
        summary = self._parse_summary()
        return KeyEvents(summary, events)

    def _parse_events(self) -> Event:
        fh = self.filehandler
        factor = 1 #TODO factor is in FxdParams. How to get it ?
        _ = UShortParser(fh).parse() # event number
        distance = UintParser(fh).parse()
        slope = UShortParser(fh).parse() * 0.001
        splice_loss = UShortParser(fh).parse() * 0.001
        refl_loss = UintParser(fh).parse() * 0.001
        evt_raw_type = fh.read(8).decode('ascii')
        evt_type = self._parse_event_type(evt_raw_type)
        return Event(
            distance=distance,
            slope=slope,
            splice_loss=splice_loss,
            refl_loss=refl_loss,
            type=evt_type,
            end_of_previous=UintParser(fh).parse(),
            start_of_current = UintParser(fh).parse(),
            end_of_current = UintParser(fh).parse(),
            start_of_next = UintParser(fh).parse(),
            peak = UintParser(fh).parse(),
            comment = StringParser(fh).parse(),
        )

    def _parse_event_type(self, evt_type: str) -> EventDataType:
        evt_type_pattern = re.compile("(.)(.)9999LS")
        match_res = evt_type_pattern.match(evt_type)
        if match_res is not None:
            subtype = match_res.groups(0)[0]
            mode = match_res.groups(0)[1]
            EventDataType(evt_type, EventType(subtype), EventModeType(mode))
        else:
            return EventDataType(evt_type, EventType.unknown, EventModeType.unknown)

    def _parse_summary(self) -> KeyEventSummary:
        factor = 1 #TODO factor is in FxdParams. How to get it ?
        return KeyEventSummary(
            total_loss=IntParser(self.filehandler).parse()*0.001,
            loss_start=IntParser(self.filehandler).parse()*factor,
            loss_end=UintParser(self.filehandler).parse()*factor,
            ORL=UShortParser(self.filehandler).parse()*0.001,
            ORL_start=IntParser(self.filehandler).parse()*factor,
            ORL_finish=UintParser(self.filehandler).parse()*factor
        )


class LnkParamsParser(BlockParser):
    def parse(self) -> BaseBlockData:
        super().parse()


class DataPtsParser(BlockParser):
    def parse(self) -> BaseBlockData:
        super().parse()


class ProprietaryBlockParser(BlockParser):
    def parse(self) -> BaseBlockData:
        super().parse()


class CksumParser(BlockParser):
    def parse(self) -> BaseBlockData:
        super().parse()
