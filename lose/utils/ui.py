# -*- coding: utf-8 -*-
import os

import libtcodpy as libtcod

from .logger import get_logger


logger = get_logger(__name__)


def create_windows(width=640, height=480):
    """Creates game windows

    Args:
        width(int): width of window
        height(int): height of window

    Returns:
        dict: mapping of game window name to window
    """
    font_bits = libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD
    package_path = __file__
    for index, path_name in enumerate(__name__.split('.')):
        if index:
            package_path = os.path.dirname(package_path)
    font_filepath = os.path.join(package_path, 'data', 'assets', 'game-font.png')
    libtcod.console_set_custom_font(font_filepath, font_bits)

    windows = {
        'root': libtcod.console_init_root(width, height, 'lose', False),
    }
    assert not libtcod.console_is_window_closed()
    logger.debug({'Created': windows})
    return windows
