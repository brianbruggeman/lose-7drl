# -*- coding: utf-8 -*-
import os

import tcod

from .keys import get_user_input
from ..logger import get_logger

logger = get_logger(__name__)


def death_menu(game_state):
    # Get game state constants
    screen_width = game_state['screen-width']
    screen_height = game_state['screen-height']
    half_width = screen_width // 2
    package_path = game_state['package-path']

    root_window = game_state['windows']['root']

    menu_title = 'You have died.'
    alpha = tcod.BKGND_SCREEN
    justification = tcod.CENTER

    # Setup Menu
    img_filename = 'game-over.png'
    img_filepath = os.path.join(package_path, 'data', 'assets', img_filename)
    img = tcod.image_load(img_filepath)

    while not tcod.console_is_window_closed():
        # show the background image, at twice the regular console resolution
        tcod.image_blit_2x(img, 0, 0, 0)

        # show the game's title, and some credits!
        tcod.console_set_default_foreground(root_window, tcod.white)
        tcod.console_set_default_background(root_window, tcod.black)
        tcod.console_print_ex(root_window, half_width, screen_height - 5, alpha, justification, menu_title)

        # show options and wait for the player's choice
        options = {}
        key, win = menu('', options, 24, game_state)
        if key:
            break


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


def main_menu(game_state, options):
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
        choice, main_menu_window = menu('Main Menu\n', options, 24, game_state)
        if choice:
            break
    return choice


def menu(header, options, width, game_state, footer=None, length=None, window=None):
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
    if options or length:
        tcod.console_set_default_foreground(window, tcod.green)
        tcod.console_print_rect_ex(window, 0, 0, width, height, tcod.BKGND_NONE, tcod.LEFT, header)

    y = header_height
    opt_index = 0
    if length:
        for each_line in range(empty):
            tcod.console_print_ex(window, 0, y + opt_index + each_line + 1, tcod.BKGND_NONE, tcod.LEFT, '')

    # print all the options
    if options:
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
    key = get_user_input()
    # get_user_input()  # for some reason there's a double input
    if key:
        logger.trace(key)
    return key, window


def msg_box(text, con, width=50):
    menu(header=text, options={}, width=width, con=con)  # use menu() as a sort of "message box"
