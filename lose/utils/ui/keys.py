# -*- coding: utf-8 -*-
import sys
import operator
from time import sleep
from random import choice, random, randint

import tcod

from ..logger import get_logger
from .messages import message

logger = get_logger(__name__)


key_mapping = {
    getattr(tcod, d): d.lower().replace('key_', '')
    for d in dir(tcod)
    if d.startswith('KEY_')
}


def get_input_info(input):
    fields = [field for field in dir(input.cdata) if not field.startswith('_')]
    info = {
        field: getattr(input.cdata, field)
        for field in fields
        if getattr(input.cdata, field, None)
    }
    # If we're using CFFI, char will be of type CDATA and will basically
    # point to a c-array of char types:  char[1]  The code below extracts
    # that data into something readable.
    char = info.get('c')
    if isinstance(char, bytes):
        char = ''.join(chr(_) for _ in char if _)
        info['c'] = char
    # If we're using CFFI, text will be of type CDATA and will basically
    # point to a c-array of char types:  char[32]  The code below extracts
    # that data into something readable.
    text = info.get('text')
    if text:
        text = ''.join(chr(v) for val in text for v in val if v)
        info['text'] = text
    return info


def get_key_string(key):
    char, char_string, mods, gen_mods = get_key_character(key)
    return char_string


def get_key_character(key, exact=False):
    mapped_key = key_mapping.get(key.vk)
    if mapped_key == 'pressed':
        mapped_key = 'escape'
    char = mapped_key if mapped_key != 'char' else chr(key.c)
    if char.endswith('win'):
        char = char.replace('win', 'meta')

    # Check modifiers
    mods = ['shift', 'lalt', 'lctrl', 'lmeta', 'rmeta', 'rctrl', 'ralt']
    found_mods = []
    for mod in mods:
        mod_value = getattr(key, mod, None)
        if mod_value is True and mod != char:
            found_mods.append(mod)
    mods = found_mods

    # Generalize modifiers
    gen_mods = ['shift', 'alt', 'ctrl', 'meta', 'win']
    found_gen_mods = []
    for gen_mod in gen_mods:
        if any(mod.endswith(gen_mod) for mod in mods):
            if gen_mod == 'win':
                gen_mod == 'meta'
            if gen_mod not in found_gen_mods:
                found_gen_mods.append(gen_mod)
    gen_mods = found_gen_mods

    # Create a string with gen_mods
    if not exact:
        char_string = '+'.join((*gen_mods, char))
    else:
        char_string = '+'.join((*mods, char))
    return char, char_string, mods, gen_mods


def get_user_input(wait=True, timeout=0.01):
    mouse = tcod.Mouse()
    key = tcod.Key()

    event_mask = tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE
    val = {}
    while not val:
        tcod.sys_check_for_event(event_mask, key, mouse)
        mouse_info = get_input_info(mouse)
        key_info = get_input_info(key)
        mouse_button = any(mouse_info[field] for field in mouse_info if 'button' in field)
        if not key.pressed and not mouse_button:
            return val
        elif not key.pressed:
            val = mouse_info
        elif key.pressed:
            val = get_key_string(key)
        if val == 'meta+text':
            val = key_info['text']
        if not wait:
            break
        sleep(timeout)
    return val


def handle_movement(game_state, position, event):
    movement_mapping = {
        'up': (-1, 0),
        'down': (1, 0),
        'left': (0, -1),
        'right': (0, 1),
        '.': (0, 0),  # rest
    }
    success = None
    if isinstance(event, dict):
        return success
    mapped_update = movement_mapping.get(event)
    if mapped_update:
        updated_position = tuple(map(operator.add, position, mapped_update))
        if process_player_move(game_state, updated_position):
            success = mapped_update
    return success


def handle_combat(game_state, position, event):
    level_map = game_state['current-level']
    combat_mapping = {
        'up': (-1, 0),
        'down': (1, 0),
        'left': (0, -1),
        'right': (0, 1),
    }
    success = None
    if isinstance(event, dict):
        return success
    mapped_update = combat_mapping.get(event)
    if mapped_update:
        tile_position = tuple(map(operator.add, position, mapped_update))
        tile = level_map.get(tile_position)
        if not tile:
            return success
        mobs = tile.get('mobs', [])
        if not mobs:
            return success
        mob = choice(mobs)
        mob_name = mob['display']['text']
        pct_to_hit = 60
        hit = (random() <= (pct_to_hit / 100))
        success = True
        if hit:
            damage = randint(1, 4)
            mob['health'] -= damage
            combat_msg = f'Player hit {mob_name} for {damage}.'
            if mob['health'] < 0:
                mob_index = tile['mobs'].index(mob)
                tile['mobs'].pop(mob_index)
                combat_msg = f'Player killed {mob_name}.'
                if not tile['mobs']:
                    tile.pop('mobs')
        else:
            combat_msg = f'Player missed.'
        message(game_state, combat_msg)
        logger.trace(combat_msg)
    return success


def handle_game_user_input(game_state):
    user_key = get_user_input()
    if user_key:
        position = game_state['character-position']
        movement_diff = handle_movement(game_state, position, user_key)
        character_action = None
        if movement_diff:
            game_state['round-updates']['character-movement'] = movement_diff
        if user_key in ['q', 'escape']:
            sys.exit()
        if user_key in ['shift+meta+d', 'shift+meta+D']:
            game_state['debug'] = not game_state['debug']
        elif not movement_diff:
            character_action = handle_combat(game_state, position, user_key)
            if character_action:
                game_state['round-updates']['character-action'] = character_action
    # if not movement_diff and not character_action:
    #     return user_key
    return user_key


def handle_keys(key_mapping):
    key = tcod.console_check_for_keypress()
    if key.vk in key_mapping.get('fullscreen'):
        # Alt+Enter: toggle fullscreen
        tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

    elif key.vk in key_mapping.get('exit'):
        return True  # exit game


def process_map_updates(game_state, updated_player_position):
    tile = game_state['current-level'].get(updated_player_position)
    tile_ref = game_state['tiles'][tile['name']]
    items = tile.get('items')
    if items:
        for item in items:
            game_state['player-inventory'].append(item)
            msg = f'Player has picked up "{item["display"]["text"]}"'
            message(game_state, msg)
            logger.debug(msg)
        tile.pop('items')
    if any(identifier in tile_ref['name'] for identifier in ['stairs', 'ladder']):
        map_name = game_state['current-map']
        map_order = game_state['map-order']
        map_index = map_order.index(map_name)
        if 'up' in tile_ref['name']:
            reverse_direction = 'down'
            new_map_index = map_index - 1
        elif 'down' in tile_ref['name']:
            reverse_direction = 'up'
            new_map_index = map_index + 1
        if new_map_index >= len(map_order):
            new_map_index = 0
        elif new_map_index < 0:
            new_map_index = len(map_order) - 1
        new_map_name = game_state['map-order'][new_map_index]
        game_state['current-map'] = new_map_name
        new_map = game_state['maps'][new_map_name]
        game_state['current-level'] = new_map
        game_state.pop('fov-map')
        possible_positions = []
        for tile_position, tile in new_map.items():
            tile_name = tile['name']
            tile_ref = game_state['tiles'][tile_name]
            if reverse_direction in tile_ref['name']:
                possible_positions.append(tile_position)
        new_player_position = choice(possible_positions)
        game_state['character-position'] = new_player_position


def process_player_move(game_state, updated_player_position):
    moved = False
    tile = game_state['current-level'].get(updated_player_position)
    if not tile:
        return moved
    tile_ref = game_state['tiles'][tile['name']]
    if tile_ref['name'] == 'closed-door':
        tile['name'] = 'open-door'
    mobs = tile.get('mobs')
    blocking = tile.get('blocking') or tile_ref.get('blocking')
    if mobs:
        pass
    elif not blocking or game_state['debug']:
        game_state['character-position'] = updated_player_position
        moved = True
        process_map_updates(game_state, updated_player_position)
    return moved


def wait_for_keypress(realtime=False):
    if realtime:
        key = tcod.console_check_for_keypress()
    else:
        key = tcod.console_wait_for_keypress(flush=True)

    char, char_string, mods, gen_mods = get_key_character(key)

    key_data = {
        'key': char_string,
        'val': key.vk,
        'pressed': key.pressed,
    }
    logger.trace(key_data)

    return char_string
