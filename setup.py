#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import os
import re
import sys
import datetime

from setuptools import setup, find_packages


def setup_project():
    '''Sets up project as needed.

    This function should be manually updated as needed.  Placed at the
    top of the file for better grokking.

    When developing, simply run (from within a virtualenv):

        $ pip install --process-dependency-links .[all]

    Returns:
        package_requires(list): List of required packages
        links(list): list of private package links
        classifiers(list): standard python package classifiers
    '''
    # Whatever dependencies package requires
    package_requires = [
        'colorama',
        'docopt',
        'libtcod-cffi',
        'pygments',
        'pyyaml',
    ]
    private_packages = [
    ]
    package_requires += private_packages

    # Links if needed for private pypi repos
    # Unfortunately, versions are not supported at the moment.
    # Currently searches only for prod.
    # TODO: Is there a way to look for dev first then prod (or vice versa)?
    links = []
    if private_packages:
        private = get_private_repo_data()
        netloc_path = 'https://{login}:{pass}@{server}/{user}/prod/'.format(**private)
        links = [
            os.path.join(netloc_path, strip_versions(required))
            for required in private_packages
            if strip_versions(required)
        ]

    return package_requires, links


# ----------------------------------------------------------------------
# Generally, only edit above this line
# ----------------------------------------------------------------------
def strip_versions(requirement):
    '''Strips out version information from package

    Args:
        requirement(str): an example of a

    Returns:
        str: Just the package name
    '''
    # Use the naive approach until we need some regex magic
    pragma = None
    if ';' in requirement:
        requirement, pragma = requirement.split(';')
    if pragma:
        if eval(pragma.strip()):
            requirement = requirement.rstrip(' <>=.,1234567890')
        else:
            requirement = ''
    return requirement


def get_private_repo_data():
    '''Loads private repo data'''
    # Dependencies
    devpi = {
        'login': os.environ.get('DEVPI_LOGIN'),
        'pass': os.environ.get('DEVPI_PASS'),
        'server': os.environ.get('DEVPI_SERVER'),
        'user': os.environ.get('DEVPI_USER'),
    }
    if not all(v for v in devpi.values()):
        err_msg = 'Devpi requires the following environment variables defined: {env_values}'
        raise RuntimeError(err_msg.format(env_values=devpi.values()))
    return devpi


def get_package_metadata(project_name=None):
    '''Captures metadata information for package

    Providing the project name will reduce the search/install time.

    Args:
        project_name: top project folder and project name

    Returns:
        dict: package metdata
    '''
    top_folder = os.path.abspath(os.path.dirname(__file__))
    required_fields = ['version', 'license', 'url', 'description', 'project']
    metadata = {}
    missing_message = []
    package_names = [p for p in find_packages() if '.' not in p]
    for root, folder, files in os.walk(top_folder):
        if not any(root.endswith(p) for p in package_names):
            continue
        for filename in files:
            if filename == '__metadata__.py':
                filepath = os.path.join(root, filename)
                relpath = filepath.replace(top_folder, '').lstrip('/')
                with open(os.path.join(filepath)) as fd:
                    exec(fd.read(), metadata)
                if 'package_metadata' in metadata:
                    metadata = metadata.get('package_metadata', {})
                if not all(field in metadata for field in required_fields):
                    missing = ', '.join(
                        field
                        for field in sorted(required_fields)
                        if field not in metadata
                    )
                    missing_message.append('{} is missing: {}'.format(relpath, missing))
                    metadata = {}
            if metadata:
                break
        if metadata:
            break
    if not metadata:
        print('Required package fields: {}'.format(', '.join(sorted(required_fields))))
        print('\n'.join(missing_message))
        raise Exception('Could not find package')
    if 'doc' not in metadata:
        if os.path.exists('README.md'):
            try:
                import pypandoc
                metadata['doc'] = pypandoc.convert('README.md', 'rst')
            except ImportError:
                with open('README.md', 'r') as fd:
                    metadata['doc'] = fd.read()
        elif os.path.exists('README.rst'):
            with open('README.rst', 'r') as fd:
                metadata['doc'] = fd.read()
    return metadata


def get_package_requirements(package_requires, links=[], required=None):
    '''Convenience function to wrap package_requires

    Args:
        required(list): list of required packages to run
    Returns:
        dict: A better format of requirements
    '''
    required = package_requires if not required else required
    requirements = {
        # Debug probably is only necessary for development environments
        'debug': [
            'ipdb',
            'ipython'
        ],

        # Deploy identifies upgrades to local system prior to deployment
        'deploy': [
            'gitpython',
        ],

        # Docs should probably only be necessary in Continuous Integration
        'docs': [
            'coverage',
            'sphinx',
            'sphinx_rtd_theme',
            'sphinxcontrib-napoleon',
        ],

        # Examples probably is only necessary for development environments
        'examples': [
            'docopt',
            'pyyaml',
        ],

        # Monitoring identifies upgrades to remote system mostly for nagios
        'monitoring': [
            'inotify',
            'psutil',
            'graphitesend',
        ],

        # private means use a known private pypi server
        'private': [
        ],

        # Requirements is the basic needs for this package
        'requirements': required,

        'setup': [],

        # Tests are needed in a local and CI environments for py.test and tox
        # Note:  To run the tox environment for docs, docs must also be installed
        'tests': [
            'detox',
            'docopt',
            'pdbpp',
            'pytest',
            'pytest-cov',
            'pytest-flake8',
            'pytest-html',
            'pytest-isort',
            'pytest-xdist',
            'pyyaml',
            'responses',
            'tox',
        ],
    }
    if sys.platform == 'darwin':
        requirements.setdefault('setup', []).append('py2app')
        requirements.setdefault('deploy', []).append('py2app')
    elif sys.platform == 'win32':
        requirements.setdefault('setup', []).append('py2exe')
        requirements.setdefault('deploy', []).append('py2exe')

    # Developers should probably run:  pip install .[dev]
    requirements['dev'] = [
        r for k, reqs in requirements.items() for r in reqs
        if k not in ['requirements']
    ]

    # All is for usability:  pip install .[all]
    requirements['all'] = [
        r for k, reqs in requirements.items() for r in reqs
    ]

    if requirements.get('private'):
        private = get_private_repo_data()
        netloc_path = 'https://{login}:{pass}@{server}/{user}/prod/'.format(**private)
        private_links = [
            os.path.join(netloc_path, strip_versions(required))
            for required in requirements['private']
            if strip_versions(required)
        ]
        links = links + private_links

    return requirements, links


def get_package_distribution_options(metadata):
    """Captures package distribution options for py2app

    For a list of options, see Apple's Runtime Configuration Guideline:

        https://developer.apple.com/library/content/documentation/MacOSX/Conceptual/BPRuntimeConfig/000-Introduction/introduction.html
    """
    project_name = metadata['project']
    version = metadata['versionstr']
    copyright_year = metadata['copyright_years']
    author = metadata['author']
    description = metadata['description']
    repo_path = os.path.dirname(os.path.abspath(__file__))
    asset_path = os.path.join(f'{project_name}', 'data', 'assets')
    options = {'py2app': {
        'bdist_base': os.path.join(f'{repo_path}', 'build'),
        'dist_dir': os.path.join(f'{repo_path}', 'dist'),
        'plist': {
            'CFBundleName': f'{project_name}',
            'CFBundleDisplayName': f'{project_name}',
            'CFBundleGetInfoString': f'{description}',
            'CFBundleIdentifier': f"org.7drl.{author}.osx.{project_name}",
            'CFBundleVersion': f"{version}",
            'CFBundleShortVersionString': f"{version}",
            'NSHumanReadableCopyright': f"Copyright © {copyright_year}, {author}, All Rights Reserved"
        },
        'argv_emulation': True,
        'iconfile': os.path.join(asset_path, 'game-icon.ico'),
    }}
    return options


def get_package_distribution_data_files(metadata):
    """Captures package distribution data files for py2app"""
    data_files = []
    project_name = metadata['project']
    data_path = os.path.join(f'{project_name}', 'data')
    for root, folders, files in os.walk(data_path):
        for filename in files:
            filepath = os.path.join(root, filename)
            data_files.append(filepath)
    return data_files


def get_console_scripts(metadata):
    '''Convenience function to wrap console scripts.

    Expects that all command-line scripts are found within the
    __main__.py file and that they are functions.

    Args:
        metadata(dict): project metadata

    Returns:
        list: scripts listed in format required by setup
    '''
    scripts = []
    project_name = metadata['project']
    project_folder = os.path.abspath(os.path.dirname(__file__))
    filepath = '{project_folder}/{project_name}/__main__.py'
    filepath = filepath.format(project_folder=project_folder, project_name=project_name)
    engine = re.compile(r"^def (?P<func>(.*?))\((?P<args>(.*?))\)\:$")
    template = '{script} = {project_name}.__main__:{func_name}'
    if os.path.exists(filepath):
        with open(filepath, 'r') as fd:
            for line in fd:
                for data in [m.groupdict() for m in engine.finditer(line)]:
                    func_name = data['func']
                    script = func_name.replace('_', '-')
                    scripts.append(template.format(script=script, project_name=project_name, func_name=func_name))
    return scripts


def main():
    '''Sets up the package'''
    metadata = get_package_metadata()
    package_requires, links = setup_project()
    requirements, links = get_package_requirements(package_requires=package_requires, links=links)
    package_distribution_options = get_package_distribution_options(metadata=metadata)
    package_distribution_data_files = get_package_distribution_data_files(metadata=metadata)
    project_name = metadata['project']
    classifiers = metadata.get('classifiers')
    extras = {k: v for k, v in requirements.items() if k != 'requirements'}
    year = metadata.get('copyright_years') or datetime.datetime.now().year
    lic = metadata.get('license') or 'Copyright {year} - all rights reserved'.format(year=year)
    # Run setup
    setup(
        # Package metadata information
        name=project_name,
        version=metadata.get('versionstr', 'unknown'),
        description=metadata.get('shortdoc') or project_name,
        long_description=metadata.get('doc') or metadata.get('shortdoc') or project_name,
        url=metadata.get('url', ''),
        license=lic,
        author=metadata.get('author', 'unknown'),
        author_email=metadata.get('email', 'unknown'),

        # Package Properties
        packages=find_packages(),
        include_package_data=True,

        # Requirements
        setup_requires=requirements.get('setup') or [],
        install_requires=requirements['requirements'],
        extras_require=extras,
        tests_require=requirements.get('tests') or [],
        dependency_links=links,
        entry_points={
            'console_scripts': get_console_scripts(metadata),
        },
        platforms=['any'],
        classifiers=classifiers,
        zip_safe=False,

        # darwin - py2app
        options=package_distribution_options,
        data_files=package_distribution_data_files,
        app=['run-lose.py'],
    )


if __name__ == '__main__':
    main()
