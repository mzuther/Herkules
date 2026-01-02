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

import operator
import pathlib
from typing import Any

import herkules.HerkulesTypes as Types


class HerkulesWorkerDiff:
    def convert_to_dict_of_dicts(
        self,
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

    def check_list_of_entries(
        self,
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

    def prepare_diff(
        self,
        original_entries: Types.EntryList | Types.EntryListJSON,
        actual_entries: Types.EntryList | Types.EntryListJSON,
        root_directory: str | pathlib.Path,
    ) -> tuple[Types.DictOfEntries, Types.DictOfEntries]:
        root_directory = pathlib.Path(
            root_directory,
        )

        self.check_list_of_entries(original_entries, 'original_entries')
        self.check_list_of_entries(actual_entries, 'actual_entries')

        original_paths = self.convert_to_dict_of_dicts(
            original_entries,
            root_directory,
        )

        actual_paths = self.convert_to_dict_of_dicts(
            actual_entries,
            root_directory,
        )

        return original_paths, actual_paths

    def diff(
        self,
        original_entries: Types.DictOfEntries,
        actual_entries: Types.DictOfEntries,
    ) -> Types.DiffResult:
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

                assert isinstance(actual_entry.mtime, float)
                assert isinstance(original_entry.mtime, float)

                if original_entry.mtime != actual_entry.mtime:
                    modified_entry = Types.HerkulesEntryDiff(
                        path=original_entry.path,
                        mtime=original_entry.mtime,
                        mtime_diff=actual_entry.mtime - original_entry.mtime,
                    )

                    differing_entries['modified'].append(modified_entry)

        for entry_id, actual_entry in actual_entries.items():
            # check for creation
            if entry_id not in original_entries:
                differing_entries['added'].append(actual_entry)

        return differing_entries
