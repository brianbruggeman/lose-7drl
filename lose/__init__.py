# -*- coding: utf-8 -*-
import os
import sys


# ----------------------------------------------------------------------
# Sometimes the environment is not actually setup, so let's try setting
# it up.  Order is important here, so do not mess up the import order.
# Having this at the top of __init__ should insure that the shared
# binary for libtcod can be found without needing to setup anything
# special.  If a LIBTCOD_DLL_PATH environment variable is already set
# then this will simply append to that variable
# ----------------------------------------------------------------------
def setup_tcod_shared_object_paths():
    dll_path_to_search = [
        os.path.abspath(os.getcwd()),
    ]
    if '__file__' in locals():
        dll_path_to_search.append(os.path.dirname(__file__))

    if sys.platform in ['darwin', 'linux']:
        dll_path_to_search.extend([
            '~/lib',
            '~/.local/lib',
            '/usr/local/lib',
            '/usr/lib',
        ])
    elif sys.platform in ['win32']:
        dll_path_to_search.extend([
            '\\Windows\\System32',
            '\\Windows',
        ])

    if 'LIBTCOD_DLL_PATH' not in os.environ:
        os.environ['LIBTCOD_DLL_PATH'] = ';'.join(dll_path_to_search)
    else:
        dll_path = os.environ.get('LIBTCOD_DLL_PATH')
        dll_path = ';'.join((dll_path, ';'.join(dll_path_to_search)))


setup_tcod_shared_object_paths()
