# -*- coding: utf-8 -*-
import os

import libtcodpy as libtcod

from ..logger import get_logger


logger = get_logger(__name__)


__all__ = ['create_windows']


def create_windows(game_state):
    """Creates game windows

    Args:
        width(int): width of window
        height(int): height of window

    Returns:
        dict: mapping of game window name to window
    """
    SCREEN_WIDTH = game_state['SCREEN_WIDTH']
    SCREEN_HEIGHT = game_state['SCREEN_HEIGHT']
    MAP_WIDTH = game_state['MAP_WIDTH']
    MAP_HEIGHT = game_state['MAP_HEIGHT']
    PANEL_WIDTH = game_state['PANEL_WIDTH']
    PANEL_HEIGHT = game_state['PANEL_HEIGHT']
    LIMIT_FPS = game_state['LIMIT_FPS']
    package_path = game_state['package_path']

    font_bits = libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW
    font_filename = 'game-font.png'
    font_filepath = os.path.join(package_path, 'data', 'assets', font_filename)
    libtcod.console_set_custom_font(font_filepath, font_bits)

    windows = {
        'root': libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'lose', False),
        'console': libtcod.console_new(MAP_WIDTH, MAP_HEIGHT),
        'panel': libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT),
    }
    game_state['windows'] = windows

    assert not libtcod.console_is_window_closed()
    libtcod.sys_set_fps(LIMIT_FPS)
    logger.debug({'Created': windows})
    return game_state
