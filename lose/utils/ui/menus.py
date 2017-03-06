# -*- coding: utf-8 -*-
import os
import libtcodpy as libtcod

from ..logger import get_logger
from .windows import create_windows

logger = get_logger(__name__)


__all__ = ['main_menu', 'menu', 'msg_box']


def main_menu(game_state):
    game_state = create_windows(game_state)

    SCREEN_WIDTH = game_state['SCREEN_WIDTH']
    SCREEN_HEIGHT = game_state['SCREEN_HEIGHT']
    MAP_WIDTH = game_state['MAP_WIDTH']
    MAP_HEIGHT = game_state['MAP_HEIGHT']
    LIMIT_FPS = game_state['LIMIT_FPS']
    PANEL_HEIGHT = game_state['PANEL_HEIGHT']
    package_path = game_state['package_path']

    font_filename = 'game-font.png'

    font_path = os.path.join(package_path, 'data', 'assets', font_filename)
    # font_bits = libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INCOL
    # font_bits = libtcod.FONT_LAYOUT_ASCII_INCOL
    font_bits = libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW
    libtcod.console_set_custom_font(font_path, flags=font_bits, nb_char_horiz=0, nb_char_vertic=0)
    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'LOSE', False)
    libtcod.sys_set_fps(LIMIT_FPS)
    con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
    panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

    img_filename = 'menu-background.png'
    img_filepath = os.path.join(package_path, 'data', 'assets', img_filename)
    img = libtcod.image_load(img_filepath)

    while not libtcod.console_is_window_closed():
        # show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)

        # show the game's title, and some credits!
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_set_default_background(0, libtcod.black)
        libtcod.console_print_ex(0, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-19, libtcod.BKGND_SCREEN, libtcod.CENTER,
                                 'LOSE: Land of Software Engineering')
        libtcod.console_print_ex(0, SCREEN_WIDTH//2, SCREEN_HEIGHT-2, libtcod.BKGND_SCREEN, libtcod.CENTER,
                                 'By Bix')

        # show options and wait for the player's choice
        options = {
            'p': 'Play a new game',
            'o': 'Options',
            'q': 'Quit',
        }
        choice = menu('', options, 24, game_state)

        if choice == 'p':  # new game
            msg_box(text='Choice is 0.\nNew Game starting.\n', con=con, width=24)
            continue
            # new_game()
            # play_game()
        elif choice == 'o':  # options
            msg_box(text='\n Choice is 1: Setting up options.\n', con=con, width=24)
            continue
        elif choice in ['q', None]:  # quit
            break


def menu(header, options, width, game_state):
    if len(options) > 26:
        raise ValueError('Cannot have a menu with more than 26 options.')

    con = game_state['windows']['console']
    SCREEN_HEIGHT = game_state['SCREEN_HEIGHT']
    SCREEN_WIDTH = game_state['SCREEN_WIDTH']

    # calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height

    # create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    # print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.green)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    # print all the options
    y = header_height
    letter_index = ord('a')
    for opt_index, opt in enumerate(options.items()):
        option_key, option_text = opt
        text = f'{option_key}: {option_text}'
        libtcod.console_print_ex(window, 0, y + opt_index, libtcod.BKGND_NONE, libtcod.LEFT, text)

    # blit the contents of "window" to the root console
    x = int(SCREEN_WIDTH / 2 - width / 2)
    y = int(SCREEN_HEIGHT / 2 - height / 2)
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    # present the root console to the player and wait for a key-press
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    if key.vk == libtcod.KEY_ENTER and key.lalt:  # (special case) Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    # convert the ASCII code to an index; if it corresponds to an option, return it

    if key.vk == libtcod.KEY_ESCAPE:
        return None
    else:
        val = chr(key.c)
        return val


def msg_box(text, con, width=50):
    menu(header=text, options={}, width=width, con=con)  # use menu() as a sort of "message box"
