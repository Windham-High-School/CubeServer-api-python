"""Time Tools
Some tools for dealing with times on microcontrollers
(to a precision of 1 second)
"""

from time import monotonic
from ._utils import Immutable

# Time unit declarations in seconds:
MINUTE = 60
HOUR   = 3600
DAY    = HOUR * 24
WEEK   = DAY * 7
YEAR   = DAY * 365

# Time zone UTC offsets:
EST    = -5 * HOUR
EDT    = -4 * HOUR

class Time(Immutable):
    """Represents an instant in time based around a UNIX timestamp"""

    # (monotonic time, epoch time) where both represent the same physical time
    _timeset = (None, None)
    _time_offset = None

    # Class Methods:
    @classmethod
    def set_unix_time(cls, unix_timestamp: int) -> None:
        cls._timeset = (int(monotonic()), int(unix_timestamp))
        cls._time_offset = int(unix_timestamp - monotonic())

    @classmethod
    def set_time(cls, current_time: 'Time') -> None:
        cls.set_unix_time(current_time.seconds)

    @classmethod
    def from_unix_time(cls, unix_time: int) -> int:
        """Returns a monotonic timestamp from a unix timestamp"""
        return int(unix_time - cls._time_offset)

    @classmethod
    def from_monotonic_time(cls, monotonic_time: int) -> int:
        """Returns a UNIX timestamp for a given monotonic time"""
        return int(monotonic_time + cls._time_offset)

    @classmethod
    def get_unix_time(cls) -> int:
        return cls.from_monotonic_time(monotonic())

    @classmethod
    def now(cls) -> 'Time':
        return cls(cls.get_unix_time())

    # Constructor and Instance Methods:
    def __init__(self, unix_timestamp: int, absolute: bool = True):
        self.seconds = unix_timestamp
        self.absolute = absolute
        super().__init__()

    def offset(self, seconds:int=0, minutes:int=0, hours:int=0, days:int=0, weeks:int=0, years:int=0) -> 'Time':
        """Offsets this time by a given amount

        Args:
            seconds (int, optional): seconds to offset by. Defaults to 0.
            minutes (int, optional): minutes to offset by. Defaults to 0.
            hours (int, optional): hours to offset by. Defaults to 0.
            days (int, optional): days to offset by. Defaults to 0.
            weeks (int, optional): weeks to offset by. Defaults to 0.
            years (int, optional): years to offset by. Defaults to 0.

        Returns:
            Time: Returns self to allow daisy-chain operations
        """
        return Time(self.seconds
            + seconds
            + minutes * MINUTE
            + hours * HOUR
            + days * DAY
            + weeks * WEEK
            + years * YEAR
        )

    def since_last(self, timeunit: int) -> 'Time':
        """Returns a Time object representing time since the beginning of the
           most recent <MINUTE|HOUR|DAY|WEEK|YEAR>

        Args:
            timeunit (int): the length, in seconds, of the specified time unit

        Returns:
            Time: the new representative Time object
        """
        return Time(
            self.seconds % timeunit,
            absolute=False
        )

    def __add__(self, other: 'Time') -> 'Time':
        if not isinstance(other, Time):
            raise TypeError(f"Cannot add {type(other)} to Time")
        return Time(
            self.seconds + other.seconds,
            absolute=False
        )

    def __sub__(self, other: 'Time') -> 'Time':
        if not isinstance(other, Time):
            raise TypeError(f"Cannot subtract {type(other)} from Time")
        return Time(
            self.seconds - other.seconds,
            absolute=False
        )

    def elapsed_since(self, other: 'Time') -> 'Time':
        """ Returns time elapsed since a given time
        """
        return self - other

    def elapsed_until(self, other: 'Time') -> 'Time':
        """ Returns time elapsed between this and a future time
        """
        return other - self

    def __mul__(self, other) -> 'Time':
        if not (isinstance(other, int) or isinstance(other, float)):
            raise TypeError(f"You can only multiply Time objects by ints and floats")
        return Time(
            self.seconds * other,
            absolute=False
        )

    def __div__(self, other) -> 'Time':
        if not (isinstance(other, int) or isinstance(other, float)):
            raise TypeError(f"You can only divide Time objects by ints and floats")
        return Time(
            self.seconds // other,
            absolute=False
        )

    def __mod__(self, other: 'Time') -> 'Time':
        if not (isinstance(other, Time) or isinstance(other, int)):
            raise TypeError(f"Cannot modulo {type(other)} with Time")
        return self.since_last(int(other))

    def __str__(self) -> str:
        if self.absolute:
            return f"{self.seconds} seconds since 1 January 1970 00:00:00 UTC"
        return f"{self.seconds} seconds"

    def __repr__(self) -> str:
        return self.__str__()

    def __abs__(self) -> 'Time':
        return Time(
            abs(self.seconds),
            self.absolute
        )

    def __int__(self) -> int:
        return self.seconds

    @property
    def monotonic(self) -> int:
        """Returns the equivalent monotonic time"""
        if self.absolute:
            return self.from_unix_time(self.seconds)
        return monotonic() + self.seconds
