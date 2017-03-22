# -*- coding: utf-8 -*-
import tcod

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
    screen_width = game_state.get('screen-width') or 80
    screen_height = game_state.get('screen-height') or 50
    map_width = game_state.get('map-width') or 72
    map_height = game_state.get('map-height') or 43
    panel_height = game_state.get('panel-height') or screen_height
    panel_width = game_state.get('panel-width') or (screen_width - map_width)
    message_width = game_state.get('message-width') or map_width
    message_height = game_state.get('message-height') or (screen_height - map_height)

    limit_fps = game_state.get('limit-fps') or 20

    windows = {
        'root': tcod.console_init_root(screen_width, screen_height, 'lose', False),
        'console': tcod.console_new(map_width, map_height),
        'panel': tcod.console_new(panel_width, panel_height),
        'messages': tcod.console_new(message_width, message_height),
    }

    assert not tcod.console_is_window_closed()
    tcod.sys_set_fps(limit_fps)
    logger.trace({'Created': windows})
    return windows
