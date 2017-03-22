# -*- coding: utf-8 -*-
import os
import copy
from random import seed, choice

from .utils.data_loaders import load_maps, load_mobs, load_items, load_tiles


def initialize_game_state(initial_seed=None, debug=False):
    """Generates a basic game state"""
    seed(initial_seed)
    if isinstance(initial_seed, str) and initial_seed.isdigit():
        initial_seed = int(initial_seed)
    game_state = {
        'screen-width': 80,
        'screen-height': 50,

        'map-width': 72,
        'map-height': 42,

        'panel-width': 20,
        'panel-height': 8,

        'message-width': 60,
        'message-height': 8,

        'limit-fps': 20,
        'fov-algorithm': 0,
        'fov-light-walls': True,
        'torch-radius': 8,
        'current-round': 0,

        'health-update': 32,
        'player-health': 1,

        'debug': debug,
        'seed': initial_seed,
        'package-path': os.path.dirname(__file__),
        'player-inventory': [
            'punch-card', 'default-pocket-protector'
        ],
    }
    load_tiles(game_state)
    load_items(game_state)
    load_mobs(game_state)
    load_maps(game_state)
    for index, item_name in enumerate(game_state.get('player-inventory', [])):
        item = copy.deepcopy(game_state['items'][item_name])
        item['equipped'] = True
        game_state['player-inventory'][index] = item

    map_name = 'town'
    level_map = game_state['maps'][map_name]
    game_state['current-map'] = map_name
    game_state['current-level'] = level_map
    game_state['map-order'] = ['town'] + sorted([k for k in game_state['maps'].keys() if k != 'town'])
    game_state['messages'] = []

    floors = [position for position, tile in level_map.items() if tile['name'] == 'floor']
    character_position = choice(floors)
    game_state['character-position'] = character_position
    return game_state
