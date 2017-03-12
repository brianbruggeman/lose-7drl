# -*- coding: utf-8 -*-
import operator
import heapq
from .distances import log_distance


def create_dijkstra_map(graph, start, target=None, cost_func=None, include_diagonals=None):
    """Creates a dijkstra map

    Args:
        graph (list): a set of nodes
        start (node): the starting position
        target (node): the ending position; None means all nodes
        cost_func (callback):  the cost function or distance formula
        include_diagonals (bool):  Only use cardinal directions if False, else include all 8 possibilities

    Returns:
        dict: mapping of node: cost
    """
    mapping = {
        node: cost
        for cost, node in dijkstra(graph, start, target=target, cost_func=cost_func, include_diagonals=include_diagonals)
    }
    return mapping


def dijkstra(graph, start, target=None, cost_func=None, include_diagonals=None):
    """Implementation of dijkstra's algorithm as a generator.

    This one uses a priority queue for a stack.

    See: https://en.wikipedia.org/wiki/Dijkstra's_algorithm

    Args:
        graph (list): a set of nodes
        start (node): the starting position
        target (node): the ending position; None means all nodes
        cost_func (callback):  the cost function or distance formula
        include_diagonals (bool):  Only use cardinal directions if False, else include all 8 possibilities

    Yields:
        cost, node
    """
    cost_func = cost_func or log_distance
    queue = []
    heapq.heapify(queue)
    costs = {start: 0}
    heapq.heappush(queue, (costs[start], start))
    yield (costs[start], start)
    while queue:
        node_cost, node = heapq.heappop(queue)
        node_cost = costs[node]
        neighbors = get_neighbors(node, include_diagonals=include_diagonals)
        neighbors = [
            neighbor for neighbor in neighbors
            if neighbor in graph  # short circuit on nodes not available
            if neighbor not in costs  # short circuit on nodes already calculated
        ]
        for neighbor in neighbors:
            neighbor_cost = cost_func(start, neighbor) + node_cost
            yield (neighbor_cost, neighbor)
            costs[neighbor] = neighbor_cost
            heapq.heappush(queue, (neighbor_cost, neighbor))
            if neighbor == target:
                break


def get_neighbors(node=None, include_diagonals=None):
    """Creates a list of neighbors.

    Yields:
        point:  a neighbor node
    """
    if node is None:
        node = (0, 0)
    cardinals = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    diagonals = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
    directions = cardinals + diagonals if include_diagonals else cardinals
    for offset in directions:
        yield tuple(map(operator.add, node, offset))
