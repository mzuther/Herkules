#!/usr/bin/env python3

# ----------------------------------------------------------------------------
#
#  Herkules
#  ========
#  Custom directory walker
#
#  Copyright (c) 2022-2025 Martin Zuther (https://www.mzuther.de/)
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

import src.herkules.HerkulesTypes as Types

__version__ = '1.2.0'


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

    # include all directories
    if modified_since is None:
        return True

    # has directory been modified?
    return (
        modification_time_in_seconds is None
        or modification_time_in_seconds >= modified_since
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

    # include all files
    if modified_since is None:
        return True

    # has file been modified?
    return (
        modification_time_in_seconds is None
        or modification_time_in_seconds >= modified_since
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
        entry['path'] = pathlib.Path(
            entry['path'].relative_to(root_directory),
        )

        entries_relative.append(entry)

    return entries_relative


def _convert_flatten_paths(
    entries: Types.EntryList,
) -> Types.EntryListFlattened:
    flattened_entries = [entry['path'] for entry in entries]

    return flattened_entries


def _convert_dict_of_dicts(
    entries: Types.EntryList,
    root_directory: pathlib.Path,
) -> Types.DictOfEntries:
    sorted_entries = sorted(
        entries,
        key=lambda k: str(k['path']),
    )

    result = {}
    for entry in sorted_entries:
        # ensure correct types
        current_path = pathlib.Path(entry['path'])
        current_mtime = float(entry['mtime'])  # type: ignore

        entry['path'] = current_path
        entry['mtime'] = current_mtime

        entry_id = str(current_path)
        result[entry_id] = entry

    return result


def herkules(
    root_directory: str | pathlib.Path,
    directories_first: bool = True,
    include_directories: bool = False,
    follow_symlinks: bool = False,
    selector: Types.Selector | None = None,
    modified_since: datetime.datetime | Types.ModificationTime = None,
    relative_to_root: bool = False,
    add_metadata: bool = False,
) -> Types.EntryList | Types.EntryListFlattened:
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
        add_metadata=add_metadata,
    )

    result: Types.EntryList | Types.EntryListFlattened = found_entries

    if relative_to_root:
        result = _convert_relative_to_root(
            found_entries,
            root_directory,
        )

    if not add_metadata:
        result = _convert_flatten_paths(
            found_entries,
        )

    return result


def _herkules_recurse(
    root_directory: pathlib.Path,
    directories_first: bool,
    include_directories: bool,
    follow_symlinks: bool,
    selector: Types.Selector,
    modified_since: Types.ModificationTime,
    add_metadata: bool,
) -> Types.EntryList:
    directories, files = _herkules_process(
        root_directory=root_directory,
        follow_symlinks=follow_symlinks,
        selector=selector,
        modified_since=modified_since,
        add_metadata=add_metadata,
    )

    # sort results
    directories.sort(key=operator.itemgetter('path'))
    files.sort(key=operator.itemgetter('path'))

    # collect results
    found_entries = []

    if not directories_first:
        found_entries.extend(files)

    # recurse
    for current_directory in directories:
        deep_found_entries = _herkules_recurse(
            root_directory=current_directory['path'],
            directories_first=directories_first,
            include_directories=include_directories,
            follow_symlinks=follow_symlinks,
            selector=selector,
            modified_since=modified_since,
            add_metadata=add_metadata,
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
    add_metadata: bool,
) -> tuple[Types.EntryList, Types.EntryList]:
    directories: Types.EntryList = []
    files: Types.EntryList = []

    # "os.scandir" minimizes system calls (including the retrieval of
    # timestamps)
    for dir_entry in os.scandir(root_directory):
        current_path = root_directory / dir_entry.name

        # "stat" is costly
        if add_metadata or modified_since:
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
                {
                    'path': current_path,
                    'mtime': modification_time_in_seconds,
                }
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
                {
                    'path': current_path,
                    'mtime': modification_time_in_seconds,
                }
            )

    return directories, files


def herkules_diff_run(
    original_entries: Types.EntryList,
    root_directory: str | pathlib.Path,
    directories_first: bool = True,
    include_directories: bool = False,
    follow_symlinks: bool = False,
    selector: Types.Selector | None = None,
    relative_to_root: bool = False,
) -> Types.DiffResult:
    actual_entries = herkules(
        root_directory=root_directory,
        directories_first=directories_first,
        include_directories=include_directories,
        follow_symlinks=follow_symlinks,
        selector=selector,
        relative_to_root=relative_to_root,
        add_metadata=True,
    )

    differing_entries = herkules_diff(
        original_entries,
        actual_entries,  # type: ignore
        root_directory,
    )

    return differing_entries


def _herkules_diff_prepare(
    original_entries: Types.EntryList,
    actual_entries: Types.EntryList,
    root_directory: str | pathlib.Path,
) -> tuple[Types.DictOfEntries, Types.DictOfEntries]:
    # entries must exist
    if len(original_entries) < 1:
        raise ValueError('"original_entries" contains no entries')

    if len(actual_entries) < 1:
        raise ValueError('"actual_entries" contains no entries')

    # entries must contain metadata; this should catch most issues without
    # impacting performance
    original_entry = original_entries[0]
    actual_entry = actual_entries[0]

    if not (isinstance(original_entry, dict) and 'mtime' in original_entry):
        raise ValueError('"original_entries" contains no metadata')

    if not (isinstance(actual_entry, dict) and 'mtime' in actual_entry):
        raise ValueError('"actual_entries" contains no metadata')

    root_directory = pathlib.Path(
        root_directory,
    )

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
    original_entries_list: Types.EntryList,
    actual_entries_list: Types.EntryList,
    root_directory: str | pathlib.Path,
) -> Types.DiffResult:
    original_entries, actual_entries = _herkules_diff_prepare(
        original_entries_list,
        actual_entries_list,
        root_directory,
    )

    differing_entries: Types.DiffResult = {
        'added': [],
        'modified': [],
        'deleted': [],
    }

    for entry_id, original_entry in original_entries.items():
        # check for deletion
        if entry_id not in actual_entries:
            differing_entries['deleted'].append(original_entry)
        # check for modification
        else:
            actual_entry = actual_entries[entry_id]

            original_mtime = original_entry['mtime']
            actual_mtime = actual_entry['mtime']

            if original_mtime != actual_mtime:
                mtime_diff = actual_mtime - original_mtime  # type: ignore

                modified_entry: Types.HerkulesEntryDiff = {
                    'path': original_entry['path'],
                    'mtime': original_entry['mtime'],
                    'mtime_diff': mtime_diff,  # type: ignore
                }

                differing_entries['modified'].append(modified_entry)

    for entry_id, actual_entry in actual_entries.items():
        # check for creation
        if entry_id not in original_entries:
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
