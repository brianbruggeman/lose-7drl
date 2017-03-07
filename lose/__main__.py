#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Provides a module level interface for running the game

Usage: lose [(-v ...)] [options]

Options:
    -w --width WIDTH     Set main window width
    -h --height HEIGHT   Set main window height
    -f --fullscreen      Run in fullscreen mode
    -C --no-color        Disable color
    -d --debug           Run in debug mode
    -r --framerate RATE  Set frame rate
    -v --verbose         Increase spam output
"""


def lose():
    from lose import runner

    docstring = __doc__
    runner(docstring=docstring, cli_arguments=None)


if __name__ == '__main__':
    lose()
