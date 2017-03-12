# -*- coding: utf-8 -*-
import os
import copy
from random import choice

import tcod
import yaml


def build_colors(game_state):
    colors = {
        'default': {
            'lit': [200, 200, 200],
            'unlit': [100, 100, 100],
        }
    }
    # Load color data
    for data in ['tiles', 'mobs', 'items']:
        if data not in game_state:
            game_state[data] = load_yaml_data(data, path=None)
        for name, entity in game_state[data].items():
            if not entity.get('display', {}).get('icon', {}).get('color'):
                entity.setdefault('display', {}).setdefault('icon', {})['color'] = colors['default']
            else:
                colors[name] = entity['display']['icon']['color']

    # Assign color data
    for entity_name, color_block in colors.items():
        for state, color in color_block.items():
            color = tcod.Color(*color)
            color_block[state] = color

    # Setup game_state
    game_state['colors'] = colors
    return game_state


def load_items(game_state, path=None):
    items = load_yaml_data(name='items', path=path)
    game_state['items'] = items
    return items


def load_level_map(game_state, map_path):
    level_map = {}
    tiles = game_state.get('tiles') or load_tiles(game_state)
    game_state['tiles'] = tiles
    game_state = game_state.get('colors') or build_colors(game_state)
    symbols = tiles['_symbols']
    if map_path.startswith('~'):
        modified_map_path = os.path.expanduser(map_path)
    else:
        modified_map_path = os.path.abspath(map_path)
    if not os.path.exists(modified_map_path):
        raise RuntimeError('Could not find map: {}'.format(map_path))

    eol_characters = ['\n']
    ignored_characters = ['\r']
    # Position
    y, x = 0, -1
    with open(map_path, 'r') as map_stream:
        for line in map_stream:
            for character in line:
                if character in ignored_characters:
                    continue
                if character in eol_characters:
                    y = y + 1
                    x = -1
                    continue
                else:
                    x = x + 1
                position = (y, x)
                tile_indices = copy.deepcopy(symbols.get(character))
                if not tile_indices:
                    raise ValueError(f'No tile found for: "{character}" at {position}')
                if len(tile_indices) == 1:
                    tile_index = tile_indices[0]
                else:
                    tile_index = choice(tile_indices)
                tile = tiles[tiles['_indices'][tile_index]]
                level_map[position] = {'name': tile['name']}
    return level_map


def load_maps(game_state, path=None):
    package_path = game_state.get('package-path')
    maps_path = os.path.join(package_path, 'data', 'maps')
    for root, folders, files in os.walk(maps_path):
        for filename in files:
            if not filename.endswith(('.map', )):
                continue
            filepath = os.path.join(root, filename)
            basename = os.path.splitext(filename)[0]
            map_data = load_level_map(game_state, filepath)
            game_state.setdefault('maps', {})[basename] = map_data


def load_mobs(game_state, path=None):
    mobs = load_yaml_data(name='mobs', path=path)
    game_state['mobs'] = mobs
    return mobs


def load_tiles(game_state, path=None):
    tiles = load_yaml_data(name='tiles', path=path)
    game_state['tiles'] = tiles
    return tiles


def load_yaml_data(name, path=None):
    data = {}
    if path is None:
        package_name = __name__.split('.')[0]
        package_path = os.path.dirname(__file__)
        while package_path.split('/')[-1] != package_name:
            package_path = os.path.dirname(package_path)
            if not package_path:
                raise RuntimeError('Could not find package-path')
        data_path = os.path.join(package_path, 'data')
        top_folder = os.path.join(data_path, name)
        for root, folders, files in os.walk(top_folder):
            for filename in files:
                if not filename.endswith(('.yaml', '.yml')):
                    continue
                filepath = os.path.join(root, filename)
                sub_data = load_yaml_data(name=name, path=filepath)
                data.update(sub_data)
    elif os.path.exists(path):
        if path.endswith(('.yaml', 'yml')):
            with open(path, 'r') as item_stream:
                yaml_data = yaml.load(item_stream.read())
                if yaml_data:
                    for data_found in yaml_data:
                        data_name = data_found['name']
                        data.setdefault(data_name, {}).update(data_found)

    # When path is None, assume we've already processed and this is the
    # tail end of the recursion.  Post fill a way to lookup by index
    # and by symbol.  This post-fill is currently ephemeral and won't
    # be saved anywhere.
    # Add indices
    if path is None:
        # This can be used to search by index.  These indices are
        # generated at runtime so they shouldn't be part of any
        # permanent storage.
        data['_indices'] = {}
        for index, data_found in enumerate(data.items()):
            data_name, data_value = data_found
            if data_name.startswith('_'):
                continue
            data_value['index'] = index
            data['_indices'][index] = data_value['name']

        # Symbols allows for lookup by symbol.  Given multiple symbols
        # for a given tile, then a random one is chosen.
        #
        # TODO: Create a Map DSL to eliminate any randomness on
        # pre-generated maps for symbols with multiple options
        data['_symbols'] = {}
        for data_name, data_value in data.items():
            if data_name == 'default':
                continue
            elif data_name.startswith('_'):
                continue
            elif not data_value.get('display', {}).get('icon', {}).get('character'):
                continue
            character = data_value['display']['icon']['character']
            data['_symbols'].setdefault(character,[]).append(data_value['index'])
    return data
