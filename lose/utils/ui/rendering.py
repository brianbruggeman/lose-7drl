# -*- coding: utf-8 -*-
import copy
from random import choice, randint

import tcod
from ..colors import get_color_map


def build_level(game_state):
    build_map(game_state)
    generate_items(game_state)
    generate_mobs(game_state)


def build_map(game_state):
    level_map = game_state.get('current-level')
    X, Y = game_state['map-width'], game_state['map-height']
    fov_map = game_state.get('fov-map') or tcod.map_new(X, Y)
    game_state['fov-map'] = fov_map
    con = game_state['windows']['console']
    tiles = game_state['tiles']

    default_tile_name = tiles['default']['ref']
    default_tile = tiles[default_tile_name]
    for y in range(Y):
        for x in range(X):
            position = (y, x)
            tile = level_map.get(position) or {'name': 'default'}
            tile_name = tile['name']
            while tiles[tile_name].get('ref', None):
                referenced_tile_name = tiles[tile_name]['ref']
                referenced_tile = tiles[referenced_tile_name]
                tile.update(referenced_tile)
                tile_name = tile['name']
            tile = tiles[tile['name']]
            if tile is None:
                tile = {}
                # Don't update the master version of the tile.
                base_tile = copy.deepcopy(default_tile)
            else:
                base_tile_name = tile.get('name')
                base_tile = tiles[base_tile_name]
            # Don't update the master version of the tile.
            blocking = tile.get('blocking') or base_tile.get('blocking')
            if not blocking:
                blocked = False
                block_sight = False
            else:
                # Tiles that block movement, implicitly also block sight
                # TODO: Make these independent
                blocking_movement = blocking.get('movement', {}).get('rate') or 0
                blocking_sight = blocking.get('sight', {}).get('opaque') or 0
                blocked = True if blocking_movement // 100 else False
                block_sight = True if blocking_sight // 100 else blocked
            tcod.map_set_properties(fov_map, x, y, not block_sight, not blocked)

    tcod.console_clear(con)  # unexplored areas start black (which is the default background color)
    return game_state['fov-map']


def clear_player(game_state):
    y, x = game_state.get('character-position')
    con = game_state['windows']['console']
    color = tcod.Color(255, 255, 124)
    # set the color and then draw the character that represents this object at its position
    tcod.console_set_default_foreground(con, color)
    tcod.console_put_char(con, x, y, ' ', tcod.BKGND_NONE)


def find_open_tiles(game_state):
    Y = game_state['map-height']
    X = game_state['map-width']
    character_position = game_state['character-position']
    open_tiles = ['floor', 'water', 'open-door']
    for y in range(Y):
        for x in range(X):
            current_tile = game_state['current-level'].get((y, x))
            if not current_tile:
                continue
            if (y, x) == character_position:
                continue
            if current_tile['name'] in open_tiles:
                mobs_on_tile = False if not current_tile.get('mobs') else True
                items_on_tile = False if not current_tile.get('items') else True
                if not mobs_on_tile and not items_on_tile:
                    yield (y, x)


def generate_mobs(game_state, number_to_create=None):
    number_to_create = number_to_create or 6
    open_tiles = list(find_open_tiles(game_state))
    number_of_mobs = randint(1, number_to_create)
    while number_of_mobs > 0:
        mob = choice([_ for _ in game_state['mobs'] if not _.startswith('_')])
        mob = copy.deepcopy(game_state['mobs'][mob])
        if 'health' not in mob:
            mob['health'] = 10
        if 'attack' not in mob:
            mob['attack'] = 3
        if 'hit-chance' not in mob:
            mob['hit-chance'] = 50
        tile_position = choice(open_tiles)
        tile = game_state['current-level'].get(tile_position)
        if not tile:
            continue
        tile.setdefault('mobs', []).append(mob)
        tile_index = open_tiles.index(tile_position)
        open_tiles.pop(tile_index)
        number_of_mobs -= 1


def generate_items(game_state, number_to_create=None):
    number_to_create = number_to_create or 6
    open_tiles = list(find_open_tiles(game_state))
    number_of_items = randint(1, number_to_create)
    while number_of_items > 0:
        item_name = choice([_ for _ in game_state['items'] if not _.startswith('_')])
        item = copy.deepcopy(game_state['items'][item_name])
        tile_position = choice(open_tiles)
        tile = game_state['current-level'].get(tile_position)
        if not tile:
            continue
        tile.setdefault('items', []).append(item)
        tile_index = open_tiles.index(tile_position)
        open_tiles.pop(tile_index)
        number_of_items -= 1


def render_bar(game_state, x, y, total_width, name, value, maximum, bar_color, back_color):
    panel = game_state['windows']['panel']
    player_health = game_state.get('player-health') or 0
    player_health_max = game_state.get('player-health-max') or 10

    # render a bar (HP, experience, etc). first calculate the width of the bar
    bar_width = int(float(player_health) / player_health_max * total_width)

    # render the background first
    tcod.console_set_default_background(panel, back_color)
    tcod.console_rect(panel, x, y, total_width, 1, False, tcod.BKGND_SCREEN)

    # now render the bar on top
    tcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        tcod.console_rect(panel, x, y, bar_width, 1, False, tcod.BKGND_SCREEN)

    # finally, some centered text with the values
    tcod.console_set_default_foreground(panel, tcod.white)
    tcod.console_print_ex(panel, x + total_width // 2, y, tcod.BKGND_NONE, tcod.CENTER,
                          name + ': ' + str(player_health) + '/' + str(player_health_max))


def render_messages(game_state):
    messages_panel = game_state['windows']['messages']
    messages = game_state['messages']

    background_color = tcod.Color(0, 0, 0)
    foreground_color = tcod.Color(127, 127, 127)
    tcod.console_set_default_background(messages_panel, background_color)
    tcod.console_set_default_foreground(messages_panel, foreground_color)
    for index, message in enumerate(messages):
        tcod.console_print_ex(messages_panel, 0, index + 1, tcod.BKGND_NONE, tcod.LEFT, message)


def render_all(game_state):
    screen_height = game_state.get('screen-height')
    screen_width = game_state.get('screen-width')
    panel_height = game_state.get('panel-height')
    panel_width = game_state.get('panel-width')
    message_height = game_state.get('message-height')
    # message_width = game_state.get('message-width')
    map_height = game_state.get('map-height')
    map_width = game_state.get('map-width')
    con = game_state['windows']['console']
    panel = game_state['windows']['panel']
    message_panel = game_state['windows']['messages']

    render_level_map(game_state)
    render_player(game_state)

    # Render panels
    panel = game_state.get('windows', {}).get('panel')

    # prepare to render the GUI panel
    tcod.console_set_default_background(panel, tcod.dark_gray)
    tcod.console_clear(panel)

    # show the player's stats
    render_bar(game_state, 0, 0, 25, 'health', 100, 100, tcod.light_red, tcod.darker_red)

    # show messages
    render_messages(game_state)

    # blit the contents of "panel" to the root console
    tcod.console_blit(message_panel, 0, 0, screen_width, message_height, 0, panel_width, screen_height - message_height)
    tcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, screen_height - panel_height)
    tcod.console_blit(con, 0, 0, map_width, map_height, 0, 0, 0)

    clear_player(game_state)
    tcod.console_flush()


def render_level_map(game_state, using_dijkstra=False):
    if 'fov-map' not in game_state:
        build_level(game_state)
    fov_map = game_state.get('fov-map')
    torch_radius = game_state.get('torch-radius')
    fov_light_walls = game_state.get('fov-light-walls')
    fov_algorithm = game_state.get('fov-algorithm')
    map_height = game_state.get('map-height')
    map_width = game_state.get('map-width')
    x, y = game_state.get('character-position')
    con = game_state['windows']['console']
    tiles = game_state.get('tiles')
    # colors = get_color_map()

    tcod.map_compute_fov(fov_map, y, x, torch_radius, fov_light_walls, fov_algorithm)
    for y in range(map_height):
        for x in range(map_width):
            lit = tcod.map_is_in_fov(fov_map, x, y)
            position = (y, x)
            tile = game_state.get('current-level', {}).get(position)
            if tile is None:
                continue
            explored = tile.get('explored')
            mobs = tile.get('mobs')
            items = tile.get('items')
            if mobs:
                mob = choice(mobs)
                tile_colors = mob['display']['icon']['color']
                character = mob['display']['icon']['character']
            elif items:
                item = choice(items)
                tile_colors = item['display']['icon']['color']
                character = item['display']['icon']['character']
            else:
                tile_colors = tile.get('color') or game_state['tiles'][tile['name']]['display']['icon']['color']
                base_tile = tiles[tile['name']]
                character = tile.get('character') or base_tile['display']['icon']['character']
            if lit:
                # look up the base tile data if it's not available in tile
                tile_color = tile_colors.get('lit') or game_state['tiles'][tile['name']][
                    'display']['icon']['color']['lit']
                tile['explored'] = True
                # tcod.console_set_char_background(con, x, y, tile_color, tcod.BKGND_SET)
                tcod.console_set_default_foreground(con, tile_color)
                tcod.console_put_char(con, x, y, character, tcod.BKGND_NONE)
            elif explored:
                tile_color = tile_colors.get('unlit') or game_state['tiles'][tile['name']][
                    'display']['icon']['color']['unlit']
                # tcod.console_set_char_background(con, x, y, tile_color, tcod.BKGND_SET)
                tcod.console_set_default_foreground(con, tile_color)
                tcod.console_put_char(con, x, y, character, tcod.BKGND_NONE)
            elif not explored:
                tile_color = tcod.Color(0, 0, 0) if not game_state['debug'] else tcod.Color(60, 45, 20)
                # tile_color = tcod.Color(125, 125, 125)
                # tcod.console_set_char_background(con, x, y, tile_color, tcod.BKGND_SET)
                tcod.console_set_default_foreground(con, tile_color)
                tcod.console_put_char(con, x, y, character, tcod.BKGND_NONE)

    tcod.console_blit(con, 0, 0, map_width, map_height, 0, 0, 0)


def render_player(game_state):
    y, x = game_state.get('character-position')
    con = game_state['windows']['console']
    color = tcod.Color(255, 255, 124)
    character = '@'
    # set the color and then draw the character that represents this object at its position
    tcod.console_set_default_foreground(con, color)
    tcod.console_put_char(con, x, y, character, tcod.BKGND_NONE)
