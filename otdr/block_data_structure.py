import logging
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List

logger = logging.getLogger("pyOTDR")


class BaseBlockData(ABC):
    """
    Syntaxic sugar to have proper type checking, all dataclass must inherit this.
    """

    pass


class BaseEnum(Enum):
    """
    For this project we need that the repr and str to be without the name of the enum just the value.
    """

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return str(self.value)


@dataclass
class Block:
    name: str
    order: int
    position: int
    size: int
    version: str


@dataclass
class MapBlock(BaseBlockData):
    """
    Dataclass where we'll feed data into. Need to be serialized with asdict()
    method
    """

    blocks: List[Block]
    version: float
    size: int


@dataclass
class SupParams(BaseBlockData):
    supplier: str = ""
    OTDR: str = ""
    OTDR_serial_number: str = ""
    module: str = ""
    module_serial_number: str = ""
    software: str = ""
    other: str = ""  # proprietary stuff.


@dataclass
class Cksum(BaseBlockData):
    file_checksum: int
    computed_checksum: int
    match: bool


@dataclass
class DataPoints(BaseBlockData):
    max_before_offset: float
    min_before_offset: float
    data_points: int
    num_traces: int
    scaling_factor: float
    points: List[float] = None  # If we don't want points.


@dataclass
class DBValue:
    value: float
    scale: str = "dB"  # I don't think it can be other than dB


@dataclass
class NsValue:
    value: int
    unit: str = "ns"


@dataclass
class MsValue:
    value: int
    unit: str = "ms"


@dataclass
class NmValue:
    value: int
    unit: str = "nm"


class LengthUnit(BaseEnum):
    mt = "meters"
    km = "kilometers"
    ft = "feet"
    kf = "kilofeet"
    mi = "miles"


@dataclass
class FxdParams(BaseBlockData):
    BC: DBValue
    EOT_threshold: DBValue
    acquisition_offset: int
    date_time: datetime
    front_panel_offset: int
    index: float
    loss_threshold: DBValue
    noise_floor_level: int
    noise_floor_scaling_factor: int
    num_average: int
    data_points: int
    number_of_pulse_width_entries: int
    power_offset_first_point: int
    pulse_width: NsValue
    range: float
    refl_threshold: DBValue
    resolution: float
    sample_spacing: MsValue
    unit: LengthUnit
    wavelength: NmValue


class FiberType(Enum):
    G651 = 651
    G652 = 652
    G653 = 653
    G654 = 654
    G655 = 655
    G656 = 656
    G657 = 657

    def __str__(self) -> str:
        return f"G.{self.value}"

    def __repr__(self) -> str:
        return f"G.{self.value}"


@dataclass
class GenParams:
    language: str = ""
    cable_id: str = ""
    fiber_id: str = ""
    cable_code: str = ""
    wavelength: NmValue = None
    comment: str = ""
    fiber_type: FiberType = None
    build_condition: str = ""
    locationA: str = ""
    locationB: str = ""
    operator: str = ""
    user_offset: int = None
    user_offset_distance: int = None


@dataclass
class KeyEventSummary:
    ORL: float = None
    ORL_start: float = None
    ORL_finish: float = None
    loss_start: float = None
    loss_end: float = None
    total_loss: float = None


class EventModeType(BaseEnum):
    A = "A"  # manual mode
    E = "E"
    F = "F"
    M = "M"
    D = "D"
    unknown = "unknown"


class EventType(BaseEnum):
    loss_drop_gain = 0
    reflection = 1
    multiple = 2  # multiple even in one key (loss+drop ?)
    unknown = -1

    def __str__(self) -> str:
        return str(self.name)

    def __repr__(self) -> str:
        return str(self.name)


@dataclass
class EventDataType:
    reference: str = None
    type: EventType = None
    mode: EventModeType = None


@dataclass
class Event:
    """
    A KeyEvent Single event
    """

    comment: str = ""
    distance: float = None
    peak: float = None
    refl_loss: float = None
    slope: float = None
    splice_loss: float = None
    end_of_previous: float = None
    start_of_current: float = None
    end_of_current: float = None
    start_of_next: float = None
    type: EventDataType = None


@dataclass
class KeyEvents:
    summary: KeyEventSummary
    events: List[Event]
