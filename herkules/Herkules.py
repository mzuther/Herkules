#!/usr/bin/env python3

# ----------------------------------------------------------------------------
#
#  Herkules
#  ========
#  Custom directory walker
#
#  Copyright (c) 2022-2026 Martin Zuther (https://www.mzuther.de/)
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions
#  are met:
#
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials provided
#     with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
#  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
#  COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
#  INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
#  STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
#  OF THE POSSIBILITY OF SUCH DAMAGE.
#
#  Thank you for using free software!
#
# ----------------------------------------------------------------------------

import datetime
import operator
import os
import pathlib
import sys
from typing import Any

import herkules.HerkulesTypes as Types

__version__ = '1.2.2'


def _is_modified(
    modified_since: Types.ModificationTime,
    modification_time_in_seconds: Types.ModificationTime,
) -> bool:
    # mtime shall not be checked
    if modified_since is None:
        return True

    # can only be None if "modified_since" is also None
    assert modification_time_in_seconds is not None

    # has file or directory been modified?
    return modification_time_in_seconds >= modified_since


def _is_directory_included(
    current_path: pathlib.Path,
    dir_entry: os.DirEntry[str],
    follow_symlinks: bool,
    selector: Types.Selector,
    modified_since: Types.ModificationTime,
    modification_time_in_seconds: Types.ModificationTime,
) -> bool:
    if not dir_entry.is_dir(follow_symlinks=follow_symlinks):
        return False

    # exclude directories
    if current_path.name in selector['excluded_directory_names']:
        return False

    return _is_modified(
        modified_since,
        modification_time_in_seconds,
    )


def _is_file_included(
    current_path: pathlib.Path,
    dir_entry: os.DirEntry[str],
    follow_symlinks: bool,
    selector: Types.Selector,
    modified_since: Types.ModificationTime,
    modification_time_in_seconds: Types.ModificationTime,
) -> bool:
    if not dir_entry.is_file(follow_symlinks=follow_symlinks):
        return False

    # exclude files
    for file_name_pattern in selector['excluded_file_names']:
        if current_path.match(file_name_pattern):
            return False

    # only include some files
    for fileglob in selector['included_file_names']:
        if current_path.match(fileglob):
            break
    else:
        return False

    return _is_modified(
        modified_since,
        modification_time_in_seconds,
    )


def _herkules_prepare(
    root_directory: str | pathlib.Path,
    selector: Types.Selector | None,
    modified_since: datetime.datetime | Types.ModificationTime,
) -> tuple[
    pathlib.Path,
    Types.Selector,
    Types.ModificationTime,
]:
    root_directory = pathlib.Path(
        root_directory,
    )

    if selector is None:
        selector = {}

    if not selector.get('excluded_directory_names'):
        selector['excluded_directory_names'] = []

    if not selector.get('excluded_file_names'):
        selector['excluded_file_names'] = []

    # include all files if no globs are specified
    if not selector.get('included_file_names'):
        selector['included_file_names'] = ['*']

    # convert to UNIX timestamp
    if isinstance(modified_since, datetime.datetime):
        modified_since = modified_since.timestamp()

    return (
        root_directory,
        selector,
        modified_since,
    )


def _convert_relative_to_root(
    entries: Types.EntryList,
    root_directory: pathlib.Path,
) -> Types.EntryList:
    entries_relative = []

    # creating a new list should be faster than modifying the existing one
    # in-place
    for entry in entries:
        entry.path = pathlib.Path(
            entry.path.relative_to(root_directory),
        )

        entries_relative.append(entry)

    return entries_relative


def _convert_flatten_paths(
    entries: Types.EntryList,
) -> Types.EntryListFlattened:
    flattened_entries = [entry.path for entry in entries]

    return flattened_entries


def _convert_dict_of_dicts(
    entries: Types.EntryList | Types.EntryListJSON,
    root_directory: pathlib.Path,
) -> Types.DictOfEntries:
    sorted_entries = sorted(
        entries,
        key=lambda k: str(operator.attrgetter('path')),
    )

    entries_as_dict: Types.DictOfEntries = {}
    for entry_original in sorted_entries:
        if isinstance(entry_original, Types.HerkulesEntry):
            entry = entry_original
        else:
            assert isinstance(entry_original, dict), (
                f'wrong type {type(entry_original)}'
            )

            entry = Types.HerkulesEntry(
                path=entry_original['path'],
                mtime=entry_original['mtime'],
            )

        entry_id = str(entry.path)
        entries_as_dict[entry_id] = entry

    return entries_as_dict


def herkules_with_metadata(
    root_directory: str | pathlib.Path,
    directories_first: bool = True,
    include_directories: bool = False,
    follow_symlinks: bool = False,
    selector: Types.Selector | None = None,
    modified_since: datetime.datetime | Types.ModificationTime = None,
    relative_to_root: bool = False,
    call_stat: bool = True,
) -> Types.EntryList:
    root_directory, selector, modified_since = _herkules_prepare(
        root_directory=root_directory,
        selector=selector,
        modified_since=modified_since,
    )

    found_entries = _herkules_recurse(
        root_directory=root_directory,
        directories_first=directories_first,
        include_directories=include_directories,
        follow_symlinks=follow_symlinks,
        selector=selector,
        modified_since=modified_since,
        call_stat=call_stat,
    )

    if relative_to_root:
        found_entries = _convert_relative_to_root(
            found_entries,
            root_directory,
        )

    return found_entries


def herkules(
    root_directory: str | pathlib.Path,
    directories_first: bool = True,
    include_directories: bool = False,
    follow_symlinks: bool = False,
    selector: Types.Selector | None = None,
    modified_since: datetime.datetime | Types.ModificationTime = None,
    relative_to_root: bool = False,
) -> Types.EntryListFlattened:
    found_entries = herkules_with_metadata(
        root_directory=root_directory,
        directories_first=directories_first,
        include_directories=include_directories,
        follow_symlinks=follow_symlinks,
        selector=selector,
        modified_since=modified_since,
        relative_to_root=relative_to_root,
        call_stat=False,
    )

    flattened_entries = _convert_flatten_paths(
        found_entries,
    )

    return flattened_entries


def _herkules_recurse(
    root_directory: pathlib.Path,
    directories_first: bool,
    include_directories: bool,
    follow_symlinks: bool,
    selector: Types.Selector,
    modified_since: Types.ModificationTime,
    call_stat: bool,
) -> Types.EntryList:
    directories, files = _herkules_process(
        root_directory=root_directory,
        follow_symlinks=follow_symlinks,
        selector=selector,
        modified_since=modified_since,
        call_stat=call_stat,
    )

    # sort results
    directories.sort(key=operator.attrgetter('path'))
    files.sort(key=operator.attrgetter('path'))

    # collect results
    found_entries = []

    if not directories_first:
        found_entries.extend(files)

    # recurse
    for current_directory in directories:
        deep_found_entries = _herkules_recurse(
            root_directory=current_directory.path,
            directories_first=directories_first,
            include_directories=include_directories,
            follow_symlinks=follow_symlinks,
            selector=selector,
            modified_since=modified_since,
            call_stat=call_stat,
        )

        if include_directories:
            found_entries.append(current_directory)

        found_entries.extend(deep_found_entries)

    if directories_first:
        found_entries.extend(files)

    return found_entries


def _herkules_process(
    root_directory: pathlib.Path,
    follow_symlinks: bool,
    selector: Types.Selector,
    modified_since: Types.ModificationTime,
    call_stat: bool,
) -> tuple[Types.EntryList, Types.EntryList]:
    directories: Types.EntryList = []
    files: Types.EntryList = []

    # "os.scandir" minimizes system calls (including the retrieval of
    # timestamps)
    for dir_entry in os.scandir(root_directory):
        current_path = root_directory / dir_entry.name

        # "stat" is costly
        if call_stat or modified_since:
            # only include paths modified after a given date; get timestamp of
            # linked path, not of symlink
            stat_result = dir_entry.stat(follow_symlinks=True)

            # "st_mtime_ns" gets the exact timestamp, although nanoseconds may
            # be missing or inexact; any file system idiosyncracies (Microsoft,
            # I mean you!) shall be handled in the client code
            modification_time_in_seconds = stat_result.st_mtime_ns / 1e9
        else:
            modification_time_in_seconds = None

        # process directories
        if _is_directory_included(
            current_path=current_path,
            dir_entry=dir_entry,
            follow_symlinks=follow_symlinks,
            selector=selector,
            modified_since=modified_since,
            modification_time_in_seconds=modification_time_in_seconds,
        ):
            directories.append(
                Types.HerkulesEntry(
                    path=current_path,
                    mtime=modification_time_in_seconds,
                )
            )
        # process files
        elif _is_file_included(
            current_path=current_path,
            dir_entry=dir_entry,
            follow_symlinks=follow_symlinks,
            selector=selector,
            modified_since=modified_since,
            modification_time_in_seconds=modification_time_in_seconds,
        ):
            files.append(
                Types.HerkulesEntry(
                    path=current_path,
                    mtime=modification_time_in_seconds,
                )
            )

    return directories, files


def herkules_diff_run(
    original_entries: Types.EntryList | Types.EntryListJSON,
    root_directory: str | pathlib.Path,
    directories_first: bool = True,
    include_directories: bool = False,
    follow_symlinks: bool = False,
    selector: Types.Selector | None = None,
    relative_to_root: bool = False,
) -> Types.DiffResult:
    actual_entries = herkules_with_metadata(
        root_directory=root_directory,
        directories_first=directories_first,
        include_directories=include_directories,
        follow_symlinks=follow_symlinks,
        selector=selector,
        relative_to_root=relative_to_root,
    )

    differing_entries = herkules_diff(
        original_entries,
        actual_entries,
        root_directory,
    )

    return differing_entries


def _herkules_type_check(
    entries: Any,
    variable_name: str,
) -> None:
    # entries must exist
    if len(entries) < 1:
        raise ValueError(f'"{variable_name}" contains no entries')

    # entries must contain metadata; this should catch most issues without
    # impacting performance
    entry = entries[0]
    contains_metadata = False

    if isinstance(entry, Types.HerkulesEntry):
        contains_metadata = True

    if isinstance(entry, dict):
        contains_metadata = 'path' in entry and 'mtime' in entry

    if not contains_metadata:
        raise ValueError(f'"{variable_name}" has wrong type {type(entry)}')


def _herkules_diff_prepare(
    original_entries: Types.EntryList | Types.EntryListJSON,
    actual_entries: Types.EntryList | Types.EntryListJSON,
    root_directory: str | pathlib.Path,
) -> tuple[Types.DictOfEntries, Types.DictOfEntries]:
    root_directory = pathlib.Path(
        root_directory,
    )

    _herkules_type_check(original_entries, 'original_entries')
    _herkules_type_check(actual_entries, 'actual_entries')

    original_paths = _convert_dict_of_dicts(
        original_entries,
        root_directory,
    )

    actual_paths = _convert_dict_of_dicts(
        actual_entries,
        root_directory,
    )

    return original_paths, actual_paths


def herkules_diff(
    original_entries_list: Types.EntryList | Types.EntryListJSON,
    actual_entries_list: Types.EntryList | Types.EntryListJSON,
    root_directory: str | pathlib.Path,
) -> Types.DiffResult:
    original_entries_dict, actual_entries_dict = _herkules_diff_prepare(
        original_entries=original_entries_list,
        actual_entries=actual_entries_list,
        root_directory=root_directory,
    )

    differing_entries: Types.DiffResult = {
        'added': [],
        'modified': [],
        'deleted': [],
    }

    for entry_id, original_entry in original_entries_dict.items():
        # check for deletion
        if entry_id not in actual_entries_dict:
            differing_entries['deleted'].append(original_entry)
        # check for modification
        else:
            actual_entry = actual_entries_dict[entry_id]

            assert isinstance(actual_entry.mtime, float)
            assert isinstance(original_entry.mtime, float)

            if original_entry.mtime != actual_entry.mtime:
                modified_entry = Types.HerkulesEntryDiff(
                    path=original_entry.path,
                    mtime=original_entry.mtime,
                    mtime_diff=actual_entry.mtime - original_entry.mtime,
                )

                differing_entries['modified'].append(modified_entry)

    for entry_id, actual_entry in actual_entries_dict.items():
        # check for creation
        if entry_id not in original_entries_dict:
            differing_entries['added'].append(actual_entry)

    return differing_entries


def main_cli() -> None:  # pragma: no coverage
    if len(sys.argv) < 2:
        print()
        print(f'version:   {__version__}')
        print()
        print(
            'HERKULES:  ME WANT EAT DIRECTORIES.  PLEASE SHOW PLACE.  '
            'THEN ME START EAT.'
        )
        print()
        print(
            'engineer:  please provide the root directory as first parameter.'
        )
        print()

        exit(1)

    SOURCE_DIR = sys.argv[1]

    SELECTOR: Types.Selector = {
        'excluded_directory_names': [],
        'excluded_file_names': [],
        'included_file_names': [],
    }

    MODIFIED_SINCE = None

    # import datetime
    # MODIFIED_SINCE = datetime.datetime(2022, 12, 1).timestamp()

    for current_path_name in herkules(
        SOURCE_DIR,
        selector=SELECTOR,
        modified_since=MODIFIED_SINCE,
    ):
        print(current_path_name)


if __name__ == '__main__':  # pragma: no coverage
    main_cli()
