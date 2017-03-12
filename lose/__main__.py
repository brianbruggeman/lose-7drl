#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Provides a module level interface for running the game

Usage: lose [(-v ...)] [options]

Options:
    -w --width WIDTH     Set main window width
    -h --height HEIGHT   Set main window height
    -f --fullscreen      Run in fullscreen mode
    -C --no-color        Disable color
    -r --framerate RATE  Set frame rate
    -v --verbose         Increase spam output
       --seed SEED       Set the seed
"""


def lose():
    from .game import runner

    docstring = __doc__
    runner(docstring=docstring, cli_arguments=None)


if __name__ == '__main__':
    lose()
