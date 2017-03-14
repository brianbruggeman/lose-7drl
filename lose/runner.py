# -*- coding: utf-8 -*-
from docopt import docopt

from .game import start_game
from .__metadata__ import __versionstr__ as version
from .utils.logger import get_logger


def handle_command_line(docstring=None, cli_arguments=None):
    version_string = f"LOSE {version} Land of Software Engineering [7drl 2017]"
    options = docopt(docstring, version=version_string, argv=cli_arguments)
    if options.get('--verbose') > 1:
        logger = get_logger('lose', 'TRACE')
    elif options.get('--verbose') > 0:
        logger = get_logger('lose', 'DEBUG')
    else:
        logger = get_logger('lose', 'INFO')

    opt_seed = options.get('--seed')
    debug = options.get('--debug')
    initial_seed = None
    if opt_seed:
        initial_seed = opt_seed
    elif debug:
        initial_seed = 10
    options['logger'] = logger
    options['--debug'] = debug
    options['--seed'] = initial_seed
    return options


def runner(docstring=None, cli_arguments=None):
    """Runs the game

    Args:
        docstring(str): Basic docstring for running the game
        cli_arguments(str): Basic command-line string
    """
    options = handle_command_line(docstring=docstring, cli_arguments=cli_arguments)
    start_game(options)
