# The story, all names, characters, and incidents portrayed in this test are
# fictitious. No identification with actual persons (living or deceased),
# places, buildings, and products is intended or should be inferred.
#
# In other words: I have great and helpful colleagues with a lot of humour. In
# order to make writing these tests more fun, I have used their (obfuscated)
# names, but all personality traits have been made up. I hope they have as much
# fun reading these tests as I had in writing them!

import datetime
import os
import pathlib
import time
from typing import cast

import pytest

import herkules.HerkulesTypes as Types
from herkules.Herkules import herkules
from tests.common import TEST_FILES, TEST_FILES_AND_DIRS, TestCommon

FIXTURE_DIR = pathlib.Path('tests') / 'beetle'


def set_mtime_to_current_time(
    dir_path: pathlib.Path,
) -> float:
    current_epoch = time.time()

    for path_in_directory in herkules(
        dir_path,
        include_directories=True,
        relative_to_root=False,
    ):
        assert isinstance(path_in_directory, pathlib.Path)

        os.utime(
            path_in_directory,
            times=(current_epoch, current_epoch),
        )

    return current_epoch


class TestBeetle(TestCommon):
    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_default_options(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        actual_paths = herkules(
            datafiles,
            relative_to_root=True,
        )

        expected_files = TEST_FILES
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_directories_in_between(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        actual_paths = herkules(
            datafiles,
            directories_first=False,
            relative_to_root=True,
        )

        expected_files = TEST_FILES[-4:]
        expected_files.extend(TEST_FILES[:-4])

        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_directories_included(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        actual_paths = herkules(
            datafiles,
            include_directories=True,
            directories_first=True,
            relative_to_root=True,
        )

        expected_files = TEST_FILES_AND_DIRS
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_directories_included_absolute(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        actual_paths = herkules(
            datafiles,
            include_directories=True,
            directories_first=True,
            relative_to_root=False,
        )

        expected_files = TEST_FILES_AND_DIRS
        self.assert_herkules_absolute(
            datafiles,
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_directories_included_in_between(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        actual_paths = herkules(
            datafiles,
            include_directories=True,
            directories_first=False,
            relative_to_root=True,
        )

        expected_files = TEST_FILES_AND_DIRS[-4:]
        expected_files.extend(TEST_FILES_AND_DIRS[:-4])

        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_selector_empty(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        SELECTOR: Types.Selector = {
            'excluded_directory_names': [],
            'excluded_file_names': [],
            'included_file_names': [],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR,
            relative_to_root=True,
        )

        expected_files = TEST_FILES
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_included_files_star_1(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        SELECTOR = {
            'excluded_directory_names': [],
            'excluded_file_names': [],
            'included_file_names': [
                '*',
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR,
            relative_to_root=True,
        )

        expected_files = TEST_FILES
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_included_files_star_2(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        SELECTOR = {
            'included_file_names': [
                '*',
                '*.txt',
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR,
            relative_to_root=True,
        )

        expected_files = TEST_FILES
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_included_files_1(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        SELECTOR = {
            'included_file_names': [
                '*.txt',
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR,
            relative_to_root=True,
        )

        expected_files = [f for f in TEST_FILES if f.endswith('.txt')]
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_included_files_2(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        SELECTOR = {
            'included_file_names': [
                '*.txt',
                '*.longext',
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR,
            relative_to_root=True,
        )

        expected_files = [
            f
            for f in TEST_FILES
            if f.endswith('.txt') or f.endswith('.longext')
        ]
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_included_files_3(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        SELECTOR = {
            'included_file_names': [
                '*.txt',
                '*.longext',
                '*.ext',
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR,
            relative_to_root=True,
        )

        expected_files = [
            f
            for f in TEST_FILES
            if f.endswith('.txt') or f.endswith('.longext')
        ]
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_included_files_4(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        SELECTOR = {
            'included_file_names': [
                '*.ext',
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR,
            relative_to_root=True,
        )

        expected_files: list[str] = []
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_included_files_6(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        SELECTOR = {
            'excluded_directory_names': [],
            'included_file_names': [
                'norm*.*',
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR,
            relative_to_root=True,
        )

        expected_files = [f for f in TEST_FILES if f.endswith('normal.txt')]
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_excluded_directories_1(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        SELECTOR = {
            'excluded_directory_names': [
                'dir.ext',
            ],
            'excluded_file_names': [],
            'included_file_names': [],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR,
            relative_to_root=True,
        )

        expected_files = [
            f for f in TEST_FILES if not f.startswith('dir.ext/')
        ]
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_excluded_directories_2(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        SELECTOR = {
            'excluded_directory_names': [
                'dir.ext',
            ],
            'excluded_file_names': [
                '.hidden.txt',
            ],
            'included_file_names': [],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR,
            relative_to_root=True,
        )

        expected_files = [
            f
            for f in TEST_FILES
            if not f.startswith('dir.ext/') and not f.endswith('.hidden.txt')
        ]
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_excluded_files_1(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        SELECTOR = {
            'excluded_directory_names': [],
            'excluded_file_names': [
                'normal.txt',
            ],
            'included_file_names': [],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR,
            relative_to_root=True,
        )

        expected_files = [
            f for f in TEST_FILES if not f.endswith('normal.txt')
        ]
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_excluded_files_2(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        SELECTOR = {
            'excluded_directory_names': [],
            'excluded_file_names': [
                '.hidden',
            ],
            'included_file_names': [],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR,
            relative_to_root=True,
        )

        expected_files = [f for f in TEST_FILES if not f.endswith('.hidden')]
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_excluded_files_3(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        SELECTOR = {
            'excluded_directory_names': [],
            'excluded_file_names': [
                '.hidden.txt',
            ],
            'included_file_names': [],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR,
            relative_to_root=True,
        )

        expected_files = [
            f for f in TEST_FILES if not f.endswith('.hidden.txt')
        ]
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_excluded_files_4(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        SELECTOR = {
            'excluded_directory_names': [],
            'excluded_file_names': [
                '.hidden.txt',
            ],
            'included_file_names': [
                '*.txt',
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR,
            relative_to_root=True,
        )

        expected_files = [
            f
            for f in TEST_FILES
            if f.endswith('.txt') and not f.endswith('.hidden.txt')
        ]
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_excluded_files_5(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        SELECTOR = {
            'excluded_directory_names': [],
            'excluded_file_names': [
                'dir.ext',
            ],
            'included_file_names': [],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR,
            relative_to_root=True,
        )

        expected_files = TEST_FILES
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_excluded_files_6(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        SELECTOR = {
            'excluded_directory_names': [],
            'excluded_file_names': [
                'norm*.*',
            ],
            'included_file_names': [],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR,
            relative_to_root=True,
        )

        expected_files = [
            f for f in TEST_FILES if not f.endswith('normal.txt')
        ]
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_excluded_files_7(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        SELECTOR = {
            'excluded_directory_names': [],
            'excluded_file_names': [
                '.hid*.txt',
            ],
            'included_file_names': [],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR,
            relative_to_root=True,
        )

        expected_files = [
            f for f in TEST_FILES if not f.endswith('.hidden.txt')
        ]
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_excluded_files_8(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        SELECTOR = {
            'excluded_directory_names': [],
            'excluded_file_names': [
                '*.ext/.hid*.txt',
            ],
            'included_file_names': [],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR,
            relative_to_root=True,
        )

        expected_files = [
            f for f in TEST_FILES if not f.endswith('dir.ext/.hidden.txt')
        ]
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_excluded_files_9(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        SELECTOR = {
            'excluded_directory_names': [],
            'excluded_file_names': [
                'dir.ext',
            ],
            'included_file_names': [],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR,
            relative_to_root=True,
        )

        expected_files = TEST_FILES
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_modified_1(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        modified_since = set_mtime_to_current_time(datafiles)

        actual_paths = herkules(
            datafiles,
            include_directories=True,
            modified_since=modified_since,
            relative_to_root=True,
        )

        expected_files = TEST_FILES_AND_DIRS
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_modified_1_in_between_directories(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        modified_since = set_mtime_to_current_time(datafiles)

        actual_paths = herkules(
            datafiles,
            directories_first=False,
            include_directories=True,
            modified_since=modified_since,
            relative_to_root=True,
        )

        expected_files = TEST_FILES_AND_DIRS[-4:]
        expected_files.extend(TEST_FILES_AND_DIRS[:-4])

        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_modified_2(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        # wait for fixture data to settle down
        modified_since = datetime.datetime.now() + datetime.timedelta(
            seconds=1
        )

        actual_paths = herkules(
            datafiles,
            include_directories=True,
            modified_since=modified_since,
            relative_to_root=True,
        )

        expected_files: list[str] = []
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.slow()
    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_modified_3(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        # wait for fixture data to settle down
        modified_since = datetime.datetime.now() + datetime.timedelta(
            seconds=0.5
        )
        time.sleep(1.0)

        new_dir = datafiles.joinpath('new.dir')
        new_dir.mkdir(parents=True)

        new_file = new_dir.joinpath('new.file.txt')
        new_file.write_text('NEW')

        actual_paths = herkules(
            datafiles,
            include_directories=True,
            modified_since=modified_since,
            relative_to_root=True,
        )

        expected_files = [
            'new.dir',
            'new.dir/new.file.txt',
        ]
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_added_metadata(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        actual_paths_with_metadata = herkules(
            datafiles,
            include_directories=True,
            directories_first=True,
            relative_to_root=True,
            add_metadata=True,
        )

        actual_paths_with_metadata = cast(
            Types.EntryList,
            actual_paths_with_metadata,
        )

        for entry in actual_paths_with_metadata:
            assert isinstance(entry['mtime'], float)

        actual_paths = [entry['path'] for entry in actual_paths_with_metadata]

        expected_files = TEST_FILES_AND_DIRS
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )
