# -*- coding: utf-8 -*-
import os
import libtcodpy as libtcod

from ..logger import get_logger
from .windows import create_windows

logger = get_logger(__name__)


__all__ = ['main_menu', 'menu', 'msg_box']


def play_game(game_state):
    map_path = 'level.map'
    dungeon_map = load_map(game_state, map_path)


def main_menu(game_state):
    game_state = create_windows(game_state)

    # Get game state constants
    SCREEN_WIDTH = game_state['SCREEN_WIDTH']
    SCREEN_HEIGHT = game_state['SCREEN_HEIGHT']
    package_path = game_state['package_path']

    # Setup Font
    font_filename = 'game-font.png'
    font_path = os.path.join(package_path, 'data', 'assets', font_filename)
    font_bits = libtcod.FONT_LAYOUT_ASCII_INROW
    libtcod.console_set_custom_font(font_path, flags=font_bits, nb_char_horiz=0, nb_char_vertic=0)

    # Setup Menu
    img_filename = 'menu-background.png'
    img_filepath = os.path.join(package_path, 'data', 'assets', img_filename)
    img = libtcod.image_load(img_filepath)

    while not libtcod.console_is_window_closed():
        # show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)

        # show the game's title, and some credits!
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_set_default_background(0, libtcod.black)
        libtcod.console_print_ex(0, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 19, libtcod.BKGND_SCREEN, libtcod.CENTER,
                                 'LOSE: Land of Software Engineering')
        libtcod.console_print_ex(0, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 2, libtcod.BKGND_SCREEN, libtcod.CENTER,
                                 'By Bix')

        # show options and wait for the player's choice
        options = {
            'p': 'Play a new game',
            'o': 'Options',
            'q': 'Quit',
        }
        choice = menu('Game Menu\n\n', options, 24, game_state)

        if choice == 'p':  # new game
            play_game(game_state)
            continue
        elif choice == 'o':  # options
            game_options = {
                'K': 'Keyboard Bindings',
                'F': 'Font',
            }
            while True:
                game_option_choice = menu('Game Options', game_options, 24, game_state)
                if game_option_choice in ['q', None]:  # quit
                    break
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
