# -*- coding: utf-8 -*-
import math
from itertools import zip_longest as lzip


def manhattan_distance(x, y):
    """Calculates the distance between x and y using the manhattan
    formula.

    This seems slower than euclidean and it is the least accurate

    Args:
        x (point): a point in space
        y (point): a point in space

    Returns:
        int:  the distance calculated between point x and point y
    """
    diffs = [abs((xval or 0) - (yval or 0)) for xval, yval in lzip(x, y)]
    return sum(diffs)


def euclidean_distance(x, y):
    """Calculates the distance between x and y using the euclidean
    formula.

    This should be the most accurate distance formula.

    Args:
        x (point): a point in space
        y (point): a point in space

    Returns:
        float:  the distance calculated between point x and point y
    """
    distance = 0
    diffs = [abs((xval or 0) - (yval or 0)) for xval, yval in lzip(x, y)]
    distance = math.sqrt(sum(diff**2 for diff in diffs))
    return distance


def octagonal_distance(x, y):
    """Calculates the distance between x and y using the octagonal
    formula.

    This is a very fast and fairly accurate approximation of the
    euclidean distance formula.
    See: http://www.flipcode.com/archives/Fast_Approximate_Distance_Functions.shtml

    Args:
        x (point): a point in space
        y (point): a point in space

    Returns:
        int:  the distance calculated between point x and point y
    """
    distance = 0
    diffs = [abs((xval or 0) - (yval or 0)) for xval, yval in lzip(x, y)]
    if len(diffs) != 2:
        raise TypeError('This distance is only valid in 2D')
    diff_min = min(diffs)
    diff_max = max(diffs)
    approximation = diff_max * 1007 + diff_min * 441
    correction = diff_max * 40 if diff_max < (diff_min << 4) else 0
    corrected_approximation = approximation - correction
    distance = (corrected_approximation + 512) >> 10
    return distance


def log_distance(x, y, func=None, k=None):
    """Calculates the distance between x and y using the octagonal
    formula.

    This wraps a distance function with a log output.  If no distance
    function is provided, then euclidean is used.

    Args:
        x (point): a point in space
        y (point): a point in space
        func (callback):  returning the log of a distance
        k (numeric): a factor  [default: 1.2]

    Returns:
        int:  the distance calculated between point x and point y
    """
    if k is None:
        k = 1.2
    if func is None:
        func = octagonal_distance
    distance = func(x, y)
    if distance == 0:
        distance = 1 / 10**10
    logged_distance = 6 * math.log(distance)
    return logged_distance
