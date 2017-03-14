# -*- coding: utf-8 -*-
import os
import heapq
from random import choice, random, randint

import tcod

from .utils.ui import menu, main_menu
from .game_state import initialize_game_state
from .utils.logger import get_logger
from .utils.ui.keys import handle_game_user_input
from .utils.ui.menus import death_menu, inventory_menu
from .utils.ui.windows import create_windows
from .utils.ui.messages import message
from .utils.ui.rendering import render_all
from .utils.algorithms.pathing import get_neighbors, create_dijkstra_map

logger = get_logger(__name__)


def initialize_game(initial_seed=None, debug=None):
    game_state = initialize_game_state(initial_seed=initial_seed, debug=debug)
    initialize_visual_library(game_state)
    game_state = create_windows(game_state)
    return game_state


def initialize_visual_library(game_state):
    package_path = game_state['package-path']

    # Setup Font
    font_filename = 'game-font.png'
    font_path = os.path.join(package_path, 'data', 'assets', font_filename)
    font_flags = tcod.FONT_LAYOUT_ASCII_INROW
    tcod.console_set_custom_font(font_path, flags=font_flags, nb_char_horiz=0, nb_char_vertic=0)


def check_for_player_action(game_state):
    action_fields = ['character-action', 'character-movement']
    action = any(field in game_state.get('round-updates', []) for field in action_fields)
    return action


def check_for_level_updates(game_state):
    round_updates = game_state.get('round-updates', [])
    position_updated = False
    for key, value in round_updates:
        if key == 'movement':
            position_updated = True
    return position_updated


def check_for_dirty_game_state(game_state):
    game_state_is_dirty = False or check_for_player_action(game_state)
    game_state_is_dirty = game_state_is_dirty or check_for_level_updates(game_state)
    return game_state_is_dirty


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
                msg = f'{mob_name} hit player for {damage}. Player has {player_health} health.'
                message(game_state, msg)
                logger.trace(msg)
                if player_health <= 0:
                    msg = 'Player has died.'
                    message(game_state, msg)
                    logger.trace(msg)
                    break
            else:
                msg = f'{mob_name} missed player. Player has {player_health} health.'
                message(game_state, msg)
                logger.trace(msg)
    game_state['player-health'] = player_health


def play_game(game_state):
    first_round = True
    while not tcod.console_is_window_closed():
        # render the screen
        setup_round(game_state)
        if first_round is True:
            first_round = False
            render_all(game_state)

        user_key = handle_game_user_input(game_state)
        if not user_key:
            continue

        # handle inventory
        if user_key in ['i', 'I']:
            item_selected, inventory_window = inventory_menu(game_state)
            tcod.console_set_default_foreground(0, tcod.white)
            tcod.console_set_default_background(0, tcod.black)

        # handle debug maps
        elif game_state['debug'] and user_key in ['shift+meta+d', 'shift+meta+D']:
            pass
            # render_djikstra_superimposed(game_state)
            # render_debug_window(game_state)

        if check_for_player_action(game_state):
            update_mob_positions(game_state)
            mob_combat(game_state)
            update_dijkstra_maps(game_state)

        if check_for_dirty_game_state(game_state):
            render_all(game_state)
        render_all(game_state)

        # handle death
        player_health = game_state.get('player-health')
        if player_health is not None and player_health <= 0:
            death_menu(game_state)
            break
    return game_state


def setup_round(game_state):
    action = check_for_player_action(game_state)
    game_state['round-updates'] = {}
    current_round = game_state['current-round']
    if current_round == 0:
        update_dijkstra_maps(game_state, force=True)
    if action:
        game_state['current-round'] += 1
        if game_state['current-round'] % game_state['health-update'] == 0:
            player_health = game_state.get('player-health') or 10
            if player_health < 10:
                player_health += 1
                logger.trace(f'Player health is: {player_health}')
            game_state['player-health'] = player_health


def start_game(options):
    logger = options['logger']
    logger.trace('Starting game')

    # Setup game
    initial_seed = options['--seed']
    debug = options['--debug']
    game_state = initialize_game(initial_seed=initial_seed, debug=debug)
    # logger.trace({'game_state': game_state})
    continue_playing = True
    while continue_playing:
        options = {
            'p': 'Play a new game',
            'o': 'Options',
            'x': 'Exit',
        }
        choice = main_menu(game_state, options)
        if choice == 'p':  # new game
            game_state = play_game(game_state)
            game_state = initialize_game(initial_seed=initial_seed, debug=debug)
            continue
        elif choice == 'o':  # options
            game_options = {
                'K': 'Keyboard Bindings',
                'F': 'Font',
                'x': 'Exit',
            }
            while continue_playing:
                game_option_choice, menu_window = menu('Game Options', game_options, 24, game_state)
                if game_option_choice in ['x', None]:  # quit
                    break
            continue
        elif choice in ['x', 'escape', None]:  # quit
            continue_playing = False
            break


def update_dijkstra_maps(game_state, force=False):
    character_position = game_state.get('character-position')
    level_map = game_state.get('current-level')
    updates = game_state['round-updates']
    movement = updates.get('character-movement')
    if movement or force:
        new_map = create_dijkstra_map(level_map, character_position)
        game_state.setdefault('dijkstra-maps', {})['character'] = new_map


def update_mob_positions(game_state, cost_threshold=5):
    character_position = game_state.get('character-position')

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
            neighbor_costs = {}
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
                    neighbor_costs.setdefault(neighbor_cost, []).append(neighbor)

            if not neighbor_costs:
                break
            neighbor_cost = min(neighbor_costs.keys())
            if neighbor_cost == 0:
                break
            updated_position = choice(neighbor_costs[neighbor_cost])
            mob_index = tile['mobs'].index(mob)
            tile['mobs'].pop(mob_index)
            if not tile['mobs']:
                tile.pop('mobs')
            level_map[updated_position].setdefault('mobs', []).append(mob)
        cost, position = heapq.heappop(cost_data)
