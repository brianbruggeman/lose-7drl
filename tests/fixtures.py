# -*- coding: utf-8 -*-
import pytest


@pytest.fixture
def font():
    """Sets up font"""
    import os
    import libtcodpy as libtcod
    import lose

    lose_path = os.path.dirname(lose.__file__)
    font_path = os.path.join(lose_path, 'data', 'assets', 'game-font.png')
    font_bits = libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD
    font = libtcod.console_set_custom_font(font_path, font_bits)
    return font_path


@pytest.fixture
def window(font):
    """Basic window for processing"""
    import libtcodpy as libtcod

    width = 80
    height = 50
    title = 'pytest window'
    fullscreen = False

    # console_init_root does not support keyword arguments - :sad panda:
    root_console = libtcod.console_init_root(width, height, title, fullscreen)
    assert root_console is None
    return root_console
