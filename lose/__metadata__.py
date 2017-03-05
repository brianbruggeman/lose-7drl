# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

__all__ = (
    '__project__', '__description__', '__versionstr__',
    '__copyright_years__', '__license__', '__url__', '__version__',
    '__classifiers__', '__keywords__', 'package_metadata',
)

# ----------------------------------------------------------------------
# Package Metadata
# ----------------------------------------------------------------------
__project__ = 'lose'
__description__ = 'Land of Software Engineering - A 7drl entry'
__versionstr__ = '0.1.0'

__copyright_years__ = '2017'
__license__ = 'Apache Software License'
__url__ = 'ssh://git@github.com/'
__version__ = tuple([int(ver_i.split('-')[0]) for ver_i in __versionstr__.split('.')])

__classifiers__ = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: Apache Software License'
    'Natural Language :: English',
    'Operating System :: MacOS',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: Implementation :: CPython',
    'Topic :: Games/Entertainment',
]

__keywords__ = ['7drl', 'roguelike']

# Package everything above into something nice and convenient for extracting
package_metadata = {k.strip('_'): v for k, v in locals().items() if k.startswith('__')}
