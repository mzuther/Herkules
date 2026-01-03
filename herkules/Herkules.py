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
import pathlib
import sys

import herkules.HerkulesTypes as Types
from herkules.HerkulesWorkerDiff import HerkulesWorkerDiff
from herkules.HerkulesWorkerFind import HerkulesWorkerFind

__version__ = '1.2.2'


class Herkules:
    def find(
        self,
        root_directory: str | pathlib.Path,
        list_directories_first: bool = True,
        include_directories: bool = False,
        follow_symlinks: bool = False,
        selector: Types.Selector | None = None,
        modified_since: datetime.datetime | Types.ModificationTime = None,
        relative_to_root: bool = False,
    ) -> Types.EntryList:
        worker_find = HerkulesWorkerFind(
            selector=selector,
            list_directories_first=list_directories_first,
            include_directories=include_directories,
            follow_symlinks=follow_symlinks,
            relative_to_root=relative_to_root,
            call_stat=True,
        )

        found_entries = worker_find.find(
            root_directory=root_directory,
            modified_since=modified_since,
        )

        return found_entries

    def find_paths_only(
        self,
        root_directory: str | pathlib.Path,
        list_directories_first: bool = True,
        include_directories: bool = False,
        follow_symlinks: bool = False,
        selector: Types.Selector | None = None,
        modified_since: datetime.datetime | Types.ModificationTime = None,
        relative_to_root: bool = False,
    ) -> Types.EntryListFlattened:
        worker_find = HerkulesWorkerFind(
            selector=selector,
            list_directories_first=list_directories_first,
            include_directories=include_directories,
            follow_symlinks=follow_symlinks,
            relative_to_root=relative_to_root,
            call_stat=False,
        )

        found_entries = worker_find.find(
            root_directory=root_directory,
            modified_since=modified_since,
        )

        flattened_entries = worker_find.flatten_paths(
            found_entries,
        )

        return flattened_entries

    def diff(
        self,
        original_entries: Types.EntryList | Types.EntryListJSON,
        actual_entries: Types.EntryList | Types.EntryListJSON,
    ) -> Types.DiffResult:
        worker_diff = HerkulesWorkerDiff()

        differing_entries = worker_diff.diff(
            original_entries_list=original_entries,
            actual_entries_list=actual_entries,
        )

        return differing_entries

    def find_and_diff(
        self,
        original_entries: Types.EntryList | Types.EntryListJSON,
        root_directory: str | pathlib.Path,
        list_directories_first: bool = True,
        include_directories: bool = False,
        follow_symlinks: bool = False,
        selector: Types.Selector | None = None,
        relative_to_root: bool = False,
    ) -> Types.DiffResult:
        actual_entries = self.find(
            root_directory=root_directory,
            list_directories_first=list_directories_first,
            include_directories=include_directories,
            follow_symlinks=follow_symlinks,
            selector=selector,
            relative_to_root=relative_to_root,
        )

        worker_diff = HerkulesWorkerDiff()

        differing_entries = worker_diff.diff(
            original_entries_list=original_entries,
            actual_entries_list=actual_entries,
        )

        return differing_entries


def herkules(
    root_directory: str | pathlib.Path,
    directories_first: bool = True,
    include_directories: bool = False,
    follow_symlinks: bool = False,
    selector: Types.Selector | None = None,
    modified_since: datetime.datetime | Types.ModificationTime = None,
    relative_to_root: bool = False,
) -> Types.EntryListFlattened:
    herkules = Herkules()

    return herkules.find_paths_only(
        root_directory=root_directory,
        list_directories_first=directories_first,
        include_directories=include_directories,
        follow_symlinks=follow_symlinks,
        selector=selector,
        modified_since=modified_since,
        relative_to_root=relative_to_root,
    )


def herkules_with_metadata(
    root_directory: str | pathlib.Path,
    directories_first: bool = True,
    include_directories: bool = False,
    follow_symlinks: bool = False,
    selector: Types.Selector | None = None,
    modified_since: datetime.datetime | Types.ModificationTime = None,
    relative_to_root: bool = False,
) -> Types.EntryList:
    herkules = Herkules()

    return herkules.find(
        root_directory=root_directory,
        list_directories_first=directories_first,
        include_directories=include_directories,
        follow_symlinks=follow_symlinks,
        selector=selector,
        modified_since=modified_since,
        relative_to_root=relative_to_root,
    )


def herkules_diff(
    original_entries_list: Types.EntryList | Types.EntryListJSON,
    actual_entries_list: Types.EntryList | Types.EntryListJSON,
) -> Types.DiffResult:
    herkules = Herkules()

    return herkules.diff(
        original_entries=original_entries_list,
        actual_entries=actual_entries_list,
    )


def herkules_diff_run(
    original_entries: Types.EntryList | Types.EntryListJSON,
    root_directory: str | pathlib.Path,
    directories_first: bool = True,
    include_directories: bool = False,
    follow_symlinks: bool = False,
    selector: Types.Selector | None = None,
    relative_to_root: bool = False,
) -> Types.DiffResult:
    herkules = Herkules()

    return herkules.find_and_diff(
        original_entries=original_entries,
        root_directory=root_directory,
        list_directories_first=directories_first,
        include_directories=include_directories,
        follow_symlinks=follow_symlinks,
        selector=selector,
        relative_to_root=relative_to_root,
    )


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
