"""Layout calculation code"""

__author__ = "Stephan Sokolow (deitarion/SSokolow)"
__license__ = "GNU GPL 2.0 or later"

import math
from heapq import heappop, heappush

# Allow MyPy to work without depending on the `typing` package
# (And silence complaints from only using the imported types in comments)
MYPY = False
if MYPY:
    # pylint: disable=unused-import
    from typing import (Any, Dict, Iterable, Iterator, List, Optional,  # NOQA
                        Sequence, Sized, Tuple, Union)

    # pylint: disable=import-error, no-name-in-module
    from gtk.gdk import Rectangle  # NOQA
    from .util import GeomTuple, PercentRect  # NOQA

    Geom = Union[Rectangle, GeomTuple]  # pylint: disable=invalid-name
del MYPY

def check_tolerance(distance, monitor_geom, tolerance=0.1):
    """Check whether a distance is within tolerance, adjusted for window size.

    @param distance: An integer value representing a distance in pixels.
    @param monitor_geom: An (x, y, w, h) tuple representing the monitor
        geometry in pixels.
    @param tolerance: A value between 0.0 and 1.0, inclusive, which represents
        a percentage of the monitor size.
    """

    # Take the euclidean distance of the monitor rectangle and convert
    # `distance` into a percentage of it, then test against `tolerance`.
    return float(distance) / math.hypot(*tuple(monitor_geom)[2:4]) < tolerance

def closest_geom_match(needle, haystack):
    # type: (Geom, Sequence[Geom]) -> Tuple[int, int]
    """Find the geometry in C{haystack} that most closely matches C{needle}.

    @return: A tuple of the euclidean distance and index in C{haystack} for the
             best match.
    """
    # Calculate euclidean distances between the window's current geometry
    # and all presets and store them in a min heap.
    euclid_distance = []  # type: List[Tuple[int, int]]
    for haystack_pos, haystack_val in enumerate(haystack):
        distance = sum([(needle_i - haystack_i) ** 2 for (needle_i, haystack_i)
                        in zip(tuple(needle), tuple(haystack_val))]) ** 0.5
        heappush(euclid_distance, (distance, haystack_pos))

    # to the next configuration. Otherwise, use the first configuration.
    closest_distance, closest_idx = heappop(euclid_distance)
    return closest_distance, closest_idx

def resolve_fractional_geom(geom_tuple, monitor_geom, win_geom=None):
    # type: (Optional[Geom], Geom, Optional[Geom]) -> Geom
    """Resolve proportional (eg. 0.5) and preserved (None) coordinates.

    @param geom_tuple: An (x, y, w, h) tuple with monitor-relative values in
                       the range from 0.0 to 1.0, inclusive.

                       If C{None}, then the value of C{win_geom} will be used.
    @param monitor_geom: An (x, y, w, h) tuple defining the bounding box of the
                       monitor (or other desired region) within the desktop.
    @param win_geom: An (x, y, w, h) tuple defining the current shape of the
                       window, in absolute desktop pixel coordinates.
    """
    monitor_geom = tuple(monitor_geom)

    if geom_tuple is None:
        return win_geom
    else:
        # Multiply x and w by monitor.w, y and h by monitor.h
        return tuple(int(i * j) for i, j in
                     zip(geom_tuple, monitor_geom[2:4] + monitor_geom[2:4]))

def make_winsplit_positions(columns):
    squares = { #x,y,w,h
        'top-left': (0.0,0.0,0.5,0.5),
        'top': (0.0,0.0,1.0,0.5),
        'top-right': (0.5,0.0,0.5,0.5),
        'left': (0.0, 0.0,0.5,1.0),
        'middle': (0.0, 0.0,1.0,1.0),
        'right': (0.5, 0.0,0.5,1.0),
        'bottom-left': (0.0, 0.5,0.5,0.5),
        'bottom': (0.0, 0.5,1.0,0.5),
        'bottom-right': (0.5,0.5,0.5,0.5),
    }
    return {k:([(x,y,w,h)]+[(x+w*i/columns,y,w/columns,h) for i in range(columns)]) for k,(x,y,w,h) in squares.items()}
