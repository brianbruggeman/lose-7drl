# -*- coding: utf-8 -*-
import os
import sys
import heapq
from random import random, randint

import tcod

from .keys import wait_for_user_input, handle_game_user_input
from ..logger import get_logger
from .windows import create_windows
from .rendering import render_all
from ..algorithms.pathing import create_dijkstra_map, get_neighbors

logger = get_logger(__name__)


def inventory_menu(game_state):
    # Setup Menu
    while not tcod.console_is_window_closed():
        # show the background image, at twice the regular console resolution
        # tcod.image_blit_2x(img, 0, 0, 0)
        header = 'Inventory'
        player_inventory_list = game_state.get('player-inventory', [])
        player_inventory = []
        for item in player_inventory_list:
            item_text = item['display']['text']
            player_inventory.append(item_text)

        options = {
            chr(index + ord('a')): item
            for index, item in enumerate(player_inventory)
        }

        choice, inventory_window = menu(header, options, 35, game_state, length=25)

        item = None
        if choice:
            item = options.get(choice, None)
        if item:
            pass
        if choice in ['escape']:
            break
    return choice, inventory_window


def main_menu(game_state):
    game_state = create_windows(game_state)

    # Get game state constants
    screen_width = game_state['screen-width']
    screen_height = game_state['screen-height']
    half_width = screen_width // 2
    half_height = screen_height // 2
    package_path = game_state['package-path']

    root_window = game_state['windows']['root']

    menu_title = 'LOSE: Land of Software Engineering'
    sub_title = 'You can be a LOSEr too!'
    footer = 'by Bix'

    alpha = tcod.BKGND_SCREEN
    justification = tcod.CENTER

    # Setup Font
    font_filename = 'game-font.png'
    font_path = os.path.join(package_path, 'data', 'assets', font_filename)
    font_flags = tcod.FONT_LAYOUT_ASCII_INROW
    tcod.console_set_custom_font(font_path, flags=font_flags, nb_char_horiz=0, nb_char_vertic=0)

    # Setup Menu
    img_filename = 'menu-background.png'
    img_filepath = os.path.join(package_path, 'data', 'assets', img_filename)
    img = tcod.image_load(img_filepath)

    while not tcod.console_is_window_closed():
        # show the background image, at twice the regular console resolution
        tcod.image_blit_2x(img, 0, 0, 0)

        # show the game's title, and some credits!
        tcod.console_set_default_foreground(root_window, tcod.light_yellow)
        tcod.console_set_default_background(root_window, tcod.black)
        tcod.console_print_ex(root_window, half_width, half_height - 19, alpha, justification, menu_title)
        tcod.console_print_ex(root_window, half_width, half_height - 17, alpha, justification, sub_title)
        tcod.console_print_ex(root_window, half_width, screen_height - 2, alpha, justification, footer)

        # show options and wait for the player's choice
        options = {
            'p': 'Play a new game',
            'o': 'Options',
            'x': 'Exit',
        }
        choice, main_menu_window = menu('Main Menu\n', options, 24, game_state)

        if choice == 'p':  # new game
            play_game(game_state)
            continue
        elif choice == 'o':  # options
            game_options = {
                'K': 'Keyboard Bindings',
                'F': 'Font',
                'x': 'Exit',
            }
            while True:
                game_option_choice, menu_window = menu('Game Options', game_options, 24, game_state, window=main_menu_window)
                if game_option_choice in ['x', None]:  # quit
                    break
            continue
        elif choice in ['x', 'escape', None]:  # quit
            break


def menu(header, options, width, game_state, footer=None, length=None, window=None):
    if len(options) > 26:
        raise ValueError('Cannot have a menu with more than 26 options.')
    empty = (length - len(options)) if length else 0
    if empty < 0:
        empty = 0

    con = game_state['windows']['console']
    screen_height = game_state['screen-height']
    screen_width = game_state['screen-width']

    # calculate total height for the header (after auto-wrap) and one line per option
    header_height = tcod.console_get_height_rect(con, 0, 0, width, screen_height, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height + (empty if length else 0)

    # create an off-screen console that represents the menu's window
    window = window or tcod.console_new(width, height)

    # print the header, with auto-wrap
    tcod.console_set_default_foreground(window, tcod.green)
    tcod.console_print_rect_ex(window, 0, 0, width, height, tcod.BKGND_NONE, tcod.LEFT, header)

    # print all the options
    y = header_height
    opt_index = 0
    if length:
        for each_line in range(empty):
            tcod.console_print_ex(window, 0, y + opt_index + each_line + 1, tcod.BKGND_NONE, tcod.LEFT, '')

    for opt_index, opt in enumerate(options.items()):
        option_key, option_text = opt
        text = f'{option_key}: {option_text}'
        tcod.console_print_ex(window, 0, y + opt_index, tcod.BKGND_NONE, tcod.LEFT, text)

    # blit the contents of "window" to the root console
    x = int(screen_width / 2 - width / 2)
    y = int(screen_height / 2 - height / 2)
    tcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    # present the root console to the player and wait for a key-press
    tcod.console_flush()
    key = wait_for_user_input()
    wait_for_user_input()  # for some reason there's a double input
    if key:
        logger.trace(key)
    return key, window


def msg_box(text, con, width=50):
    menu(header=text, options={}, width=width, con=con)  # use menu() as a sort of "message box"


def play_game(game_state):
    while not tcod.console_is_window_closed():
        # render the screen

        setup_round(game_state)

        render_all(game_state)
        tcod.console_flush()

        user_key = handle_game_user_input(game_state)
        update_mob_positions(game_state)
        mob_combat(game_state)
        update_dijkstra_maps(game_state)

        # handle inventory
        if user_key in ['i', 'I']:
            item_selected, inventory_window = inventory_menu(game_state)
            tcod.console_set_default_foreground(0, tcod.white)
            tcod.console_set_default_background(0, tcod.black)

        # handle debug maps
        elif game_state['debug'] and user_key in ['shift+meta+d', 'shift+meta+D']:
            pass
            # render_debug_window(game_state)

        # # erase all objects at their old locations, before they move
        # for object in objects:
        #     object.clear()

        # # handle keys and exit game if needed
        # player_action = handle_keys()
        # if player_action == 'exit':
        #     save_game()
        #     break

        # # let monsters take their turn
        # if game_state == 'playing' and player_action != 'didnt-take-turn':
        #     for object in objects:
        #         if object.ai:
        #             object.ai.take_turn()


def update_dijkstra_maps(game_state, force=False):
    character_position = game_state.get('character-position')
    level_map = game_state.get('current-level')
    updates = game_state['round-updates']
    movement = updates.get('character-movement')
    if movement or force:
        new_map = create_dijkstra_map(level_map, character_position)
        game_state.setdefault('dijkstra-maps', {})['character'] = new_map


def setup_round(game_state):
    action = game_state.get('character-action') or game_state.get('round-updates', {}).get('character-movement')
    game_state.pop('character-action', None)
    game_state.pop('character-movement', None)
    game_state['round-updates'] = {}
    if game_state['current-round'] == 0:
        update_dijkstra_maps(game_state, force=True)
    if action:
        game_state['current-round'] += 1
        if game_state['current-round'] % 16 == 0:
            player_health = game_state.get('player-health') or 10
            if player_health < 10:
                player_health += 1
                logger.trace('Player health is: {player_health}')
            game_state['player-health'] = player_health


def update_mob_positions(game_state, cost_threshold=30):
    updates = game_state['round-updates']
    action = game_state.get('character-action') or updates.get('character-movement')

    character_position = game_state.get('character-position')
    if not action:
        return

    character_map = game_state['dijkstra-maps']['character']
    level_map = game_state['current-level']
    tiles = game_state['tiles']
    cost_data = []
    heapq.heapify(cost_data)
    for position, cost in character_map.items():
        data = cost, position
        heapq.heappush(cost_data, (data))

    cost, position = heapq.heappop(cost_data)
    while cost <= cost_threshold:
        tile = level_map[position]
        mobs = tile.get('mobs', [])
        for mob in mobs:
            neighbor_costs = []
            for neighbor in get_neighbors(position, include_diagonals=True):
                neighbor_tile = level_map[neighbor]
                neighbor_cost = character_map[neighbor]
                base_tile = tiles[neighbor_tile['name']]
                blocks_movement = False
                has_entity = False
                if neighbor == character_position:
                    has_entity = True
                elif neighbor_tile.get('mobs'):
                    has_entity = True
                if neighbor_tile.get('blocking', {}).get('movement', {}).get('rate') == 100:
                    blocks_movement = True
                elif base_tile.get('blocking', {}).get('movement', {}).get('rate') == 100:
                    blocks_movement = True
                if not blocks_movement and not has_entity:
                    neighbor_costs.append((neighbor_cost, neighbor))

            neighbor_cost, updated_position = min(neighbor_costs)
            mob_index = tile['mobs'].index(mob)
            tile['mobs'].pop(mob_index)
            if not tile['mobs']:
                tile.pop('mobs')
            level_map[updated_position].setdefault('mobs', []).append(mob)
        cost, position = heapq.heappop(cost_data)


def mob_combat(game_state):
    updates = game_state['round-updates']
    action = game_state.get('character-action') or updates.get('character-movement')
    character_position = game_state.get('character-position')
    player_health = game_state.get('player-health') or 10
    if not action:
        return

    level_map = game_state['current-level']
    for neighbor in get_neighbors(character_position, include_diagonals=True):
        neighbor_tile = level_map[neighbor]
        mobs = neighbor_tile.get('mobs', [])
        for mob in mobs:
            mob_name = mob['display']['text']
            mob_hit_chance = mob.get('hit-chance')
            mob_attack = mob.get('attack')
            hit = (random() >= (1 - mob_hit_chance / 100))
            if hit:
                damage = randint(1, mob_attack)
                player_health = player_health - damage
                logger.trace(f'{mob_name} hit player for {damage}. Player has {player_health}.')
                if player_health <= 0:
                    logger.trace('Player has died.')
                    sys.exit()
            else:
                logger.trace(f'{mob_name} missed player. Player has {player_health}.')
    game_state['player-health'] = player_health

