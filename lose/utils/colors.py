# -*- coding: utf-8 -*-
import os

from tcod import Color

colors = {
    '': ''
}


def get_color_map():
    pass


def load_colors(game_state):
    package_path = game_state['package-path']
    color_tree = os.path.join(package_path, 'data', 'colors')

    for root, folders, files in os.walk(color_tree):
        pass
