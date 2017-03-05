#!/usr/bin/env bash
#
# Sets up git hooks for this project
#
top_repo_folder=$(git rev-parse --show-toplevel)
git_hooks_folder=$top_repo_folder/.git/hooks
tools_hooks_folder=$top_repo_folder/tools/git

# Setup pre-commit
if [ ! -f $git_hooks_folder/pre-commit ]; then
    ln -s $tools_hooks_folder/multihooks.py $git_hooks_folder/pre-commit
else
    echo "WARNING: Could not copy over existing .git/hooks/pre-commit"
fi
if [ ! -d $git_hooks_folder/pre-commit.d ]; then
    ln -s $tools_hooks_folder/pre-commit.d $git_hooks_folder/pre-commit.d
else
    echo "WARNING: Could not copy over existing .git/hooks/pre-commit.d folder"
fi
