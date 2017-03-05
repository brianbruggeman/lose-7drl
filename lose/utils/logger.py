# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import json
import logging
import datetime

import yaml
import colorama
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import Terminal256Formatter

# Required for colored output
colorama.init()

#  Additional logging levels
ALL = 2
TRACE = 5
FATAL = logging.CRITICAL + 10

# Add names as well
logging.addLevelName(ALL, 'ALL')
logging.addLevelName(TRACE, 'TRACE')
logging.addLevelName(FATAL, 'FATAL')

# Map names to levels
log_name_mapping = {
    d: getattr(logging, d)
    for d in dir(logging)
    if d.upper() == d and isinstance(getattr(logging, d), int)
}

# Add new levels
log_name_mapping['ALL'] = ALL
log_name_mapping['TRACE'] = TRACE
log_name_mapping['FATAL'] = FATAL

# Supplement mapping levels to names
# log_name_mapping now contains all names and levels as keys
log_name_mapping.update({v: v for k, v in log_name_mapping.items()})


def log_all(self, message, *args, **kwds):
    if self.isEnabledFor(ALL):
        self.log(ALL, message, *args, **kwds)


def log_trace(self, message, *args, **kwds):
    if self.isEnabledFor(TRACE):
        self.log(TRACE, message, *args, **kwds)


def log_fatal(self, message, *args, **kwds):
    if self.isEnabledFor(FATAL):
        self.log(FATAL, message, *args, **kwds)


def get_logger(logname, level=None):
    """Default logging setup

    Args:
        logname(str): name of logger
        level(int or str): level of logger

    Return:
        logger.Logger: the logger requested
    """
    if isinstance(level, str):
        level = level.upper()
    level = log_name_mapping.get(level) or level
    level = logging.INFO if not isinstance(level, int) else level

    # Add new levels
    logging.Logger.all = log_all
    logging.Logger.trace = log_trace
    logging.Logger.fatal = log_fatal

    root_name = logname.split('.')[0]
    root_logger = logging.getLogger(root_name)
    logger = logging.getLogger(logname)

    # setup root logger
    root_logger.setLevel(level)
    logger.setLevel(level)

    add_custom_handler = True
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            add_custom_handler = False

    if add_custom_handler:
        handler = logging.StreamHandler()
        formatter = CustomFormatter()
        handler.setFormatter(formatter)
        handler.setLevel(ALL)
        logger.addHandler(handler)

    return logger


class CustomFormatter(logging.Formatter):

    '''Modifies the level prefix of the log with the following level
    information:

    !!! - critical
     !  - error
     ?  - warn
        - info
     -  - debug
    '''
    default_prefix = '???'  # used with non-generic levels

    PYGMENTS_LEXER = JsonLexer()
    PYGMENTS_FORMATTER = Terminal256Formatter()

    color_mapping = {
        FATAL: colorama.Fore.RED + colorama.Style.BRIGHT,
        logging.CRITICAL: colorama.Fore.RED + colorama.Style.NORMAL,
        logging.ERROR: colorama.Fore.RED + colorama.Style.NORMAL,
        logging.WARNING: colorama.Fore.YELLOW + colorama.Style.NORMAL,
        logging.INFO: colorama.Fore.CYAN + colorama.Style.NORMAL,
        logging.DEBUG: colorama.Fore.GREEN + colorama.Style.NORMAL,
        TRACE: colorama.Fore.GREEN + colorama.Style.DIM,
        ALL: colorama.Style.DIM,
    }

    prefix_mapping = {

        FATAL: '!!!',
        logging.CRITICAL: '.!.',
        logging.ERROR: ' ! ',
        logging.WARNING: ' ? ',
        logging.INFO: ' - ',
        logging.DEBUG: ' . ',
        TRACE: ' ' * 3,
        ALL: ' ' * 3,
    }

    def highlight_message(self, record):
        # Capture relevant record data
        # Setup/Disable colors if needed
        color = self.color_mapping.get(record.levelno) or ''
        dim = colorama.Style.DIM
        reset = colorama.Fore.RESET + colorama.Style.RESET_ALL
        emphasis = colorama.Style.BRIGHT if record.levelno > logging.CRITICAL else ''
        level = self.prefix_mapping.get(record.levelno) or self.default_prefix
        msg = self.update_message_for_objects(record.msg)
        data = dict(
            level=level,
            msecs=datetime.datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S"),

            # Setup colors
            color=color,
            dim=dim,
            reset=reset,
            name=record.name,
            func=record.funcName,
            emphasis=emphasis
        )

        # Format msg
        prefix = '{color}{level}{reset} {dim}{msecs}{reset} {color}[{name}]{reset}{emphasis}'
        prefix = prefix.format(**data)
        dmsg = []
        for m in msg.split('\n'):
            m = highlight(m, self.PYGMENTS_LEXER, self.PYGMENTS_FORMATTER).rstrip('\n')
            dmsg.append(m)
        dmsg = '\n'.join(dmsg)
        data.update(locals().items())
        template = prefix + ' {msg}' + colorama.Fore.RESET + colorama.Style.RESET_ALL
        new_msg = '\n'.join(template.format(msg=m) for m in dmsg.split('\n'))
        new_msg = new_msg.rstrip('\n')
        return new_msg

    def update_message_for_objects(self, msg):
        if not isinstance(msg, str):
            try:
                msg = yaml.safe_dump(msg, indent=4, default_flow_style=False)
            except:
                try:
                    msg = json.dumps(msg, indent=4, sort_keys=True)
                except:
                    msg = str(msg)
        return msg

    def format(self, record):
        # msg = super(CustomFormatter, self).format(record)
        msg = self.highlight_message(record)

        # Dump
        return msg
