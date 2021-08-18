import pkgutil

from .southwest import Reservation
from .openflights import timezone_for_airport

__library_name__ = "southwest"
__version__ = pkgutil.get_data(__library_name__, "VERSION").decode("utf-8")
