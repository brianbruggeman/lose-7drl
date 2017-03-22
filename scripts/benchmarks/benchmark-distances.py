#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from lose.utils.algorithms.distances import euclidean_distance, manhattan_distance, octagonal_distance
from lose.utils.algorithms.distances.distances import euclidean_distance as py_euclidean
from lose.utils.algorithms.distances.distances import manhattan_distance as py_manhattan
from lose.utils.algorithms.distances.distances import octagonal_distance as py_octagonal


def benchmark_distance_function(name, dist, number=None):
    x = (1, 1)
    y = (2, 2)

    number = number or 1000000  # 1 million only takes a few seconds
    start = time.time()
    values = [dist(x, y) for _ in range(number)]
    end = time.time()
    diff = end - start
    length = len(values)
    print(f'{name} Ran in {diff} seconds generating {length} records.')


print('-' * 40)
# Euclidean
benchmark_distance_function(' C-Ext Euclidean Distance', euclidean_distance)

# Pure Python Euclidean
benchmark_distance_function('Python Euclidean Distance', py_euclidean)

print('-' * 40)
# Manhattan
benchmark_distance_function(' C-Ext Manhattan Distance', manhattan_distance)

# Pure Python Manhattan
benchmark_distance_function('Python Manhattan Distance', py_manhattan)

print('-' * 40)
# Octagonal
benchmark_distance_function(' C-Ext Octagonal Distance', octagonal_distance)

# Pure Python Octagonal
benchmark_distance_function('Python Octagonal Distance', py_octagonal)
