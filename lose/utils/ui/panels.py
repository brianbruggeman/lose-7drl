# -*- coding: utf-8 -*-
import libtcodpy as libtcod

from ..logger import get_logger


logger = get_logger(__name__)


__all__ = ['Panel']


class Panel(object):
    """Creates a panel on the screen.

    Args:
        width(int): Width of panel [default: 80]
        height(int): height of panel [default: 50]
        name(str): Title of panel  [default: Untitled]
        position(tuple): (int: y, int: x) position on parent [default: (0, 0)]
        parent(int): parent object of panel [default: root]
    """

    def __init__(self, width=None, height=None, name=None, position=None, parent=None):
        self.width = width or 80
        self.height = height or 50
        self.name = name or 'Untitled'
        self.position = position or (0, 0)
        self.parent = parent
        self.panel = libtcod.console_new(self.width, self.height)

    def __repr__(self):
        cname = self.__class__.__name__
        name = self.name
        size = (self.width, self.height)
        position = self.position
        string = f'<{cname} {name} [{position} -> ({size})]>'
        return string
