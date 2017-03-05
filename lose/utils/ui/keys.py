# -*- coding: utf-8 -*-
import libtcodpy as libtcod

from ..logger import get_logger


logger = get_logger(__name__)


def handle_keys(key_mapping):
    key = libtcod.console_check_for_keypress()
    if key.vk in key_mapping.get('fullscreen'):
        # Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk in key_mapping.get('exit'):
        return True  # exit game

    # elif key.vk in key_mapping.get('move-left'):
