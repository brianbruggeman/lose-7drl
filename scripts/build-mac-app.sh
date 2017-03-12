#!/usr/bin/env bash
#
# Runs a mac build using py2app
#
top_repo_folder=$(git rev-parse --show-toplevel)

cd $top_repo_folder
python setup.py py2app -A
