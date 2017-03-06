# -*- coding: utf-8 -*-
import os

import libtcodpy as libtcod
from docopt import docopt

from .utils import *  # noqa
from .__metadata__ import __versionstr__ as version


def initialize_game():
    """Generates a basic game state"""
    game_state = {
        'SCREEN_WIDTH': 80,
        'SCREEN_HEIGHT': 43,
        'MAP_WIDTH': 80,
        'MAP_HEIGHT': 43,
        'PANEL_HEIGHT': 7,
        'PANEL_WIDTH': 43,
        'LIMIT_FPS': 20,
        'package_path': os.path.dirname(__file__),
    }
    return game_state


def game_menu(game_state):
    """Creates the initial game menu"""
    panel = Panel()

    header_height = libtcod.console_get_height_rect(panel.parent, 0, 0, width, height, header)


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

    game_state = initialize_game()
    game_state['logger'] = logger
    logger.debug({'game_state': game_state})
    main_menu(game_state)
