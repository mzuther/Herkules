import difflib
import pathlib
import sys

import pytest

import herkules.HerkulesTypes as Types

TEST_FILES = [
    '.hiddendir/.hidden',
    '.hiddendir/.hidden.txt',
    '.hiddendir/multi.dot.longext',
    '.hiddendir/normal.txt',
    # ---
    '.hiddendir.ext/.hidden',
    '.hiddendir.ext/.hidden.txt',
    '.hiddendir.ext/multi.dot.longext',
    '.hiddendir.ext/normal.txt',
    # ---
    'dir.ext/.hidden',
    'dir.ext/.hidden.txt',
    'dir.ext/multi.dot.longext',
    'dir.ext/normal.txt',
    # ---
    'directory/.hidden',
    'directory/.hidden.txt',
    'directory/multi.dot.longext',
    'directory/normal.txt',
    # ---
    '.hidden',
    '.hidden.txt',
    'multi.dot.longext',
    'normal.txt',
]

TEST_FILES_AND_DIRS = []

for entry in TEST_FILES:
    if entry.endswith('/.hidden'):
        TEST_FILES_AND_DIRS.append(
            entry.removesuffix('/.hidden'),
        )

    TEST_FILES_AND_DIRS.append(entry)


class TestCommon:
    def assert_herkules_absolute(
        self,
        root_path,
        expected_files,
        actual_paths,
    ):
        actual_paths_relative = []
        for actual_path in actual_paths:
            actual_path_relative = actual_path.relative_to(root_path)
            actual_paths_relative.append(
                pathlib.Path(actual_path_relative),
            )

        return self.assert_herkules_relative(
            expected_files,
            actual_paths_relative,
        )

    def assert_herkules_relative(
        self,
        expected_files,
        actual_paths,
    ):
        for actual_path in actual_paths:
            assert isinstance(
                actual_path,
                pathlib.Path,
            )

        # force identical output, regardless of operating system
        actual_files = [str(pathlib.Path(f)) for f in actual_paths]
        expected_files = [str(pathlib.Path(f)) for f in expected_files]

        if actual_files != expected_files:  # pragma: no coverage
            # force well-formatted diff output
            expected_files = '\n'.join(expected_files) + '\n'
            actual_files = '\n'.join(actual_files) + '\n'

            diff_result = difflib.unified_diff(
                expected_files.splitlines(keepends=True),
                actual_files.splitlines(keepends=True),
                fromfile='EXPECTED',
                tofile='ACTUAL',
            )

            print('------------------------------------------------------')
            print()
            print('Difference between expected and actual output:')
            print()
            sys.stdout.writelines(diff_result)
            print()

            pytest.fail('Found differing files.')

    def create_herkules_entry_from_path(
        self,
        absolute_path,
        root_directory,
    ):
        stat_result = absolute_path.stat(follow_symlinks=True)
        modification_time_in_seconds = stat_result.st_mtime_ns / 1e9

        entry = {
            'path': pathlib.Path(
                absolute_path.relative_to(root_directory),
            ),
            'mtime': modification_time_in_seconds,
        }

        return entry
