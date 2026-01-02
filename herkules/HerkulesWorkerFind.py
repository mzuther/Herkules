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

import herkules.HerkulesTypes as Types


class HerkulesWorkerFind:
    def is_path_modified(
        self,
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

    def is_directory_included(
        self,
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

        return self.is_path_modified(
            modified_since,
            modification_time_in_seconds,
        )

    def is_file_included(
        self,
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

        return self.is_path_modified(
            modified_since,
            modification_time_in_seconds,
        )

    def convert_relative_to_root(
        self,
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

    def prepare_find(
        self,
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

    def find_by_recursion(
        self,
        root_directory: pathlib.Path,
        directories_first: bool,
        include_directories: bool,
        follow_symlinks: bool,
        selector: Types.Selector,
        modified_since: Types.ModificationTime,
        call_stat: bool,
    ) -> Types.EntryList:
        directories, files = self.process_directory(
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
            deep_found_entries = self.find_by_recursion(
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

    def process_directory(
        self,
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
                # only include paths modified after a given date; get
                # timestamp of linked path, not of symlink
                stat_result = dir_entry.stat(follow_symlinks=True)

                # "st_mtime_ns" gets the exact timestamp, although nanoseconds
                # may be missing or inexact; any file system idiosyncracies
                # (Microsoft, I mean you!) shall be handled in the client code
                modification_time_in_seconds = stat_result.st_mtime_ns / 1e9
            else:
                modification_time_in_seconds = None

            # process directories
            if self.is_directory_included(
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
            elif self.is_file_included(
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
