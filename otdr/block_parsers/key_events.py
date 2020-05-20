import logging
import re

from otdr.block_data_structure import (
    KeyEvents,
    Event,
    EventDataType,
    EventType,
    EventModeType,
    KeyEventSummary,
)
from otdr.block_parsers.abstract_parser import BlockParser
from otdr.type_parser import (
    UintParser,
    UShortParser,
    StringParser,
    IntParser,
)

logger = logging.getLogger("pyOTDR")


class KeyEventParser(BlockParser):


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
        factor = 1  # TODO factor is in FxdParams. How to get it ?
        return KeyEventSummary(
            total_loss=IntParser(self.filehandler).parse() * 0.001,
            loss_start=IntParser(self.filehandler).parse() * factor,
            loss_end=UintParser(self.filehandler).parse() * factor,
            ORL=UShortParser(self.filehandler).parse() * 0.001,
            ORL_start=IntParser(self.filehandler).parse() * factor,
            ORL_finish=UintParser(self.filehandler).parse() * factor,
        )

class KeyEventsParserV1(KeyEventParser):
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
        factor = 1  # TODO factor is in FxdParams. How to get it ?
        _ = UShortParser(fh).parse()  # event number
        distance = UintParser(fh).parse()
        slope = UShortParser(fh).parse() * 0.001
        splice_loss = UShortParser(fh).parse() * 0.001
        refl_loss = UintParser(fh).parse() * 0.001
        evt_raw_type = fh.read(8).decode("ascii")
        evt_type = self._parse_event_type(evt_raw_type)
        return Event(
            distance=distance,
            slope=slope,
            splice_loss=splice_loss,
            refl_loss=refl_loss,
            type=evt_type,
            comment=StringParser(fh).parse(),
        )

class KeyEventsParserV2(KeyEventParser):
    def parse(self) -> KeyEvents:
        super().parse()
        fh = self.filehandler
        block_name = fh.read(len("KeyEvents") + 1).decode("ascii")
        if block_name != "KeyEvents\0":
            raise ValueError(f"Block name should be KeyEvents got {block_name}")
        number_of_events = UShortParser(fh).parse()
        logger.debug(f"{number_of_events=}")
        events = list()
        for e in range(number_of_events):
            events.append(self._parse_events())
        summary = self._parse_summary()
        return KeyEvents(summary, events)

    def _parse_events(self) -> Event:
        fh = self.filehandler
        factor = 1  # TODO factor is in FxdParams. How to get it ?
        _ = UShortParser(fh).parse()  # event number
        distance = UintParser(fh).parse()
        slope = UShortParser(fh).parse() * 0.001
        splice_loss = UShortParser(fh).parse() * 0.001
        refl_loss = UintParser(fh).parse() * 0.001
        evt_raw_type = fh.read(8).decode("ascii")
        evt_type = self._parse_event_type(evt_raw_type)
        return Event(
            distance=distance,
            slope=slope,
            splice_loss=splice_loss,
            refl_loss=refl_loss,
            type=evt_type,
            end_of_previous=UintParser(fh).parse(),
            start_of_current=UintParser(fh).parse(),
            end_of_current=UintParser(fh).parse(),
            start_of_next=UintParser(fh).parse(),
            peak=UintParser(fh).parse(),
            comment=StringParser(fh).parse(),
        )


