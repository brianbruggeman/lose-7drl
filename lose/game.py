# -*- coding: utf-8 -*-
import os
import copy
from random import seed, choice

from docopt import docopt

from .utils.ui import main_menu
from .__metadata__ import __versionstr__ as version
from .utils.logger import get_logger
from .utils.data_loaders import load_maps, load_mobs, load_items, load_tiles


def initialize_game(initial_seed=None, debug=False):
    """Generates a basic game state"""
    seed(initial_seed)
    if isinstance(initial_seed, str) and initial_seed.isdigit():
        initial_seed = int(initial_seed)
    game_state = {
        'screen-width': 80,
        'screen-height': 43,
        'map-width': 72,
        'map-height': 42,
        'panel-height': 7,
        'panel-width': 43,
        'limit-fps': 20,
        'fov-algorithm': 0,
        'fov-light-walls': True,
        'torch-radius': 8,
        'current-round': 0,

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

    map_name = 'level0'
    level_map = game_state['maps'][map_name]
    game_state['current-level'] = level_map

    floors = [position for position, tile in level_map.items() if tile['name'] == 'floor']
    character_position = choice(floors)
    game_state['character-position'] = character_position
    return game_state


def runner(docstring=None, cli_arguments=None):
    """Runs the game

    Args:
        docstring(str): Basic docstring for running the game
        cli_arguments(str): Basic command-line string
    """
    version_string = f"LOSE {version} Land of Software Engineering [7drl 2017]"
    options = docopt(docstring, version=version_string, argv=cli_arguments)
    if options.get('--verbose') > 1:
        logger = get_logger('lose', 'TRACE')
    elif options.get('--verbose') > 0:
        logger = get_logger('lose', 'DEBUG')
    else:
        logger = get_logger('lose', 'INFO')

    opt_seed = options.get('--seed')
    debug = options.get('--debug')
    initial_seed = None
    if opt_seed:
        initial_seed = opt_seed
    elif debug:
        initial_seed = 10
    game_state = initialize_game(initial_seed=initial_seed, debug=debug)
    logger.trace('Starting game')
    # logger.trace({'game_state': game_state})
    main_menu(game_state)
