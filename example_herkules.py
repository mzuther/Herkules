#!/usr/bin/env python3

# %% Imports
import datetime
import pathlib
import time

import herkules.HerkulesTypes as Types
from herkules.Herkules import herkules_diff_run, herkules_with_metadata

# %% Initialization
# directory to be crawled (can also be a string)
ROOT_DIRECTORY = pathlib.Path('./tests/')

# optional: return directories and their contents before regular files
DIRECTORIES_FIRST = True

# optional: whether subdirectories should be included in the output; their
# contents will always be crawled, however, regardless of this setting
INCLUDE_DIRECTORIES = False

# optional: include files and directories which are symlinks
FOLLOW_SYMLINKS = False

# globs: https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.match
SELECTOR: Types.Selector = {
    # optional: directories that should not be crawled (full name is matched)
    'excluded_directory_names': [
        '.git',
        '.mypy_cache',
        '.ruff_cache',
        '.pytest_cache',
        '.venv',
    ],
    # optional: file names that should be included in the result (glob)
    'excluded_file_names': [
        '*.*c',
    ],
    # optional: file names that should be excluded from the result (glob,
    # "*" by default)
    'included_file_names': [],
}

# optional: only include directories and files with were modified at or past
# the given time; for symlinks, this checks the original file
MODIFIED_SINCE = datetime.datetime(2024, 8, 1, 8, 30, 0)

# optional: if "False" (default), return paths relative to current directory;
# otherwise, return paths relative to "ROOT_DIRECTORY"
RELATIVE_TO_ROOT = False

# %% Crawl directory

# get list of dictonaries with keys "path" and "mtime" (modification time);
# for a simple list of paths, use "herkules()" instead
contents = herkules_with_metadata(
    root_directory=ROOT_DIRECTORY,
    directories_first=DIRECTORIES_FIRST,
    include_directories=INCLUDE_DIRECTORIES,
    follow_symlinks=FOLLOW_SYMLINKS,
    selector=SELECTOR,
    modified_since=MODIFIED_SINCE,
    relative_to_root=RELATIVE_TO_ROOT,
)

print()
print('Found files:')
print()

for entry in contents:
    print(f'* {entry.path}')
print()

# fake creation of two files
del contents[3]
del contents[12]

# modify a file
contents[1].path.touch(exist_ok=True)

# fake deletion of file
deleted_file = Types.HerkulesEntry(
    path=pathlib.Path('tests/trash/~deleted.txt'),
    mtime=time.time(),
)

contents.append(deleted_file)

# %% Find differences between former run and current state
differing_entries = herkules_diff_run(
    original_entries=contents,
    root_directory=ROOT_DIRECTORY,
    directories_first=DIRECTORIES_FIRST,
    include_directories=INCLUDE_DIRECTORIES,
    follow_symlinks=FOLLOW_SYMLINKS,
    selector=SELECTOR,
    relative_to_root=RELATIVE_TO_ROOT,
)

print('Changed files:')

for category in differing_entries:
    print()
    print(f'[{category}]')

    for entry in differing_entries[category]:  # type: ignore  # simplify code
        print(f'* {entry.path}')

print()
