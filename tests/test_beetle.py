# The story, all names, characters, and incidents portrayed in this test are
# fictitious. No identification with actual persons (living or deceased),
# places, buildings, and products is intended or should be inferred.
#
# In other words: I have great and helpful colleagues with a lot of humour. In
# order to make writing these tests more fun, I have used their (obfuscated)
# names, but all personality traits have been made up. I hope they have as much
# fun reading these tests as I had in writing them!

import datetime
import json
import os
import pathlib
import time

import pytest

from src.herkules.Herkules import herkules, herkules_diff, herkules_diff_run

from .common import TestCommon

FIXTURE_DIR = pathlib.Path('tests') / 'beetle'

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


def set_mtime_to_current_time(
    dir_path,
):
    current_epoch = time.time()

    for path_in_directory in herkules(
        dir_path,
        include_directories=True,
        relative_to_root=False,
    ):
        os.utime(
            path_in_directory,
            times=(current_epoch, current_epoch),
        )

    return current_epoch


class TestBeetle(TestCommon):
    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_default_options(
        self,
        datafiles,
    ):
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
        datafiles,
    ):
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
        datafiles,
    ):
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
        datafiles,
    ):
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
        datafiles,
    ):
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
        datafiles,
    ):
        SELECTOR = {
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
        datafiles,
    ):
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
        datafiles,
    ):
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
        datafiles,
    ):
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
        datafiles,
    ):
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
        datafiles,
    ):
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
        datafiles,
    ):
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

        expected_files = []
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_included_files_6(self, datafiles):
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
        datafiles,
    ):
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
        datafiles,
    ):
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
        datafiles,
    ):
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
        datafiles,
    ):
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
        datafiles,
    ):
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
        datafiles,
    ):
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
        datafiles,
    ):
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
        datafiles,
    ):
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
        datafiles,
    ):
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
        datafiles,
    ):
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
        datafiles,
    ):
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
        datafiles,
    ):
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
        datafiles,
    ):
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
        datafiles,
    ):
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

        expected_files = []
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.slow()
    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_modified_3(
        self,
        datafiles,
    ):
        # wait for fixture data to settle down
        modified_since = datetime.datetime.now() + datetime.timedelta(
            seconds=1
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
        datafiles,
    ):
        actual_paths_with_metadata = herkules(
            datafiles,
            include_directories=True,
            directories_first=True,
            relative_to_root=True,
            add_metadata=True,
        )

        for entry in actual_paths_with_metadata:
            assert isinstance(entry['mtime'], float)

        actual_paths = [entry['path'] for entry in actual_paths_with_metadata]

        expected_files = TEST_FILES_AND_DIRS
        self.assert_herkules_relative(
            expected_files,
            actual_paths,
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_no_changes(
        self,
        datafiles,
    ):
        original_paths = herkules(
            datafiles,
            relative_to_root=True,
            add_metadata=True,
        )

        # simulate loading original files from storage (paths as *strings*)
        original_files = json.loads(
            json.dumps(
                original_paths,
                default=str,
                indent=2,
            )
        )

        differing_files = herkules_diff_run(
            original_files,
            datafiles,
            relative_to_root=True,
        )

        assert differing_files['added'] == []
        assert differing_files['deleted'] == []
        assert differing_files['modified'] == []

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_error_handling_no_entries_1(
        self,
        datafiles,
    ):
        correct_paths = herkules(
            datafiles,
            add_metadata=True,
        )

        no_paths = []

        with pytest.raises(ValueError) as exc_info:
            herkules_diff(
                no_paths,
                correct_paths,
                datafiles,
            )

        assert (
            exc_info.value.args[0]
            == '"original_paths_or_files" contains no entries'
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_error_handling_no_entries_2(
        self,
        datafiles,
    ):
        correct_paths = herkules(
            datafiles,
            add_metadata=True,
        )

        no_paths = []

        with pytest.raises(ValueError) as exc_info:
            herkules_diff(
                correct_paths,
                no_paths,
                datafiles,
            )

        assert (
            exc_info.value.args[0]
            == '"actual_paths_or_files" contains no entries'
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_error_handling_no_metadata_1(
        self,
        datafiles,
    ):
        correct_paths = herkules(
            datafiles,
            add_metadata=True,
        )

        flattened_paths = herkules(
            datafiles,
            add_metadata=False,
        )

        with pytest.raises(ValueError) as exc_info:
            herkules_diff(
                flattened_paths,
                correct_paths,
                datafiles,
            )

        assert (
            exc_info.value.args[0]
            == '"original_paths_or_files" contains no metadata'
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_error_handling_no_metadata_2(
        self,
        datafiles,
    ):
        correct_paths = herkules(
            datafiles,
            add_metadata=True,
        )

        flattened_paths = herkules(
            datafiles,
            add_metadata=False,
        )

        with pytest.raises(ValueError) as exc_info:
            herkules_diff(
                correct_paths,
                flattened_paths,
                datafiles,
            )

        assert (
            exc_info.value.args[0]
            == '"actual_paths_or_files" contains no metadata'
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_no_changes_with_folders(
        self,
        datafiles,
    ):
        original_paths = herkules(
            datafiles,
            relative_to_root=True,
            include_directories=True,
            directories_first=True,
            add_metadata=True,
        )

        # simulate loading original files from storage (paths as *strings*)
        original_files = json.loads(
            json.dumps(
                original_paths,
                default=str,
                indent=2,
            )
        )

        differing_files = herkules_diff_run(
            original_files,
            datafiles,
            relative_to_root=True,
            include_directories=True,
            directories_first=False,
        )

        assert differing_files['added'] == []
        assert differing_files['deleted'] == []
        assert differing_files['modified'] == []

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_create_file(
        self,
        datafiles,
    ):
        original_paths = herkules(
            datafiles,
            relative_to_root=True,
            add_metadata=True,
        )

        # create file
        created_path = datafiles / 'this.is/a_present'
        created_path.parent.mkdir(exist_ok=False)
        created_path.touch(exist_ok=False)

        created_entry = self.create_herkules_entry_from_path(
            created_path,
            root_directory=datafiles,
        )

        differing_files = herkules_diff_run(
            original_paths,
            datafiles,
            relative_to_root=True,
        )

        assert differing_files['added'] == [
            created_entry,
        ]

        assert differing_files['deleted'] == []
        assert differing_files['modified'] == []

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_create_folder(
        self,
        datafiles,
    ):
        original_paths = herkules(
            datafiles,
            relative_to_root=True,
            include_directories=True,
            directories_first=True,
            add_metadata=True,
        )

        # create file
        created_path = datafiles / 'this.is/a_present'
        created_path.parent.mkdir(exist_ok=False)
        created_path.touch(exist_ok=False)

        created_folder = self.create_herkules_entry_from_path(
            created_path.parent,
            root_directory=datafiles,
        )

        created_entry = self.create_herkules_entry_from_path(
            created_path,
            root_directory=datafiles,
        )

        differing_files = herkules_diff_run(
            original_paths,
            datafiles,
            include_directories=True,
            directories_first=True,
            relative_to_root=True,
        )

        assert differing_files['added'] == [
            created_folder,
            created_entry,
        ]

        assert differing_files['deleted'] == []
        assert differing_files['modified'] == []

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_create_folder_separate_run(
        self,
        datafiles,
    ):
        original_paths = herkules(
            datafiles,
            relative_to_root=True,
            include_directories=True,
            directories_first=False,
            add_metadata=True,
        )

        # create file
        created_path = datafiles / 'this.is/a_present'
        created_path.parent.mkdir(exist_ok=False)
        created_path.touch(exist_ok=False)

        created_folder = self.create_herkules_entry_from_path(
            created_path.parent,
            root_directory=datafiles,
        )

        created_entry = self.create_herkules_entry_from_path(
            created_path,
            root_directory=datafiles,
        )

        actual_paths = herkules(
            datafiles,
            relative_to_root=True,
            include_directories=True,
            directories_first=True,
            add_metadata=True,
        )

        differing_files = herkules_diff(
            original_paths,
            actual_paths,
            datafiles,
        )

        assert differing_files['added'] == [
            created_folder,
            created_entry,
        ]

        assert differing_files['deleted'] == []
        assert differing_files['modified'] == []

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_rename_file(
        self,
        datafiles,
    ):
        original_paths = herkules(
            datafiles,
            relative_to_root=True,
            add_metadata=True,
        )

        renamed_path_original = datafiles / TEST_FILES[11]
        renamed_path_current = datafiles / 'moved.to/new.home'

        renamed_entry_original = self.create_herkules_entry_from_path(
            renamed_path_original,
            root_directory=datafiles,
        )

        # rename file
        renamed_path_current.parent.mkdir(exist_ok=False)
        renamed_path_original.rename(renamed_path_current)

        renamed_entry_current = self.create_herkules_entry_from_path(
            renamed_path_current,
            root_directory=datafiles,
        )

        differing_files = herkules_diff_run(
            original_paths,
            datafiles,
            relative_to_root=True,
        )

        assert differing_files['added'] == [
            renamed_entry_current,
        ]

        assert differing_files['deleted'] == [
            renamed_entry_original,
        ]

        assert differing_files['modified'] == []

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_delete_file(
        self,
        datafiles,
    ):
        original_paths = herkules(
            datafiles,
            relative_to_root=True,
            add_metadata=True,
        )

        deleted_path = datafiles / TEST_FILES[6]

        deleted_entry = self.create_herkules_entry_from_path(
            deleted_path,
            root_directory=datafiles,
        )

        # delete file
        deleted_path.unlink(missing_ok=False)

        differing_files = herkules_diff_run(
            original_paths,
            datafiles,
            relative_to_root=True,
        )

        assert differing_files['deleted'] == [
            deleted_entry,
        ]

        assert differing_files['added'] == []
        assert differing_files['modified'] == []

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_delete_folder(
        self,
        datafiles,
    ):
        original_paths = herkules(
            datafiles,
            relative_to_root=False,
            include_directories=True,
            directories_first=False,
            add_metadata=True,
        )

        deleted_folder_name = 'dir.ext'
        deleted_folder_path = datafiles / deleted_folder_name

        deleted_entries = []
        for entry in original_paths:
            entry_path = entry['path']

            if entry_path.is_dir() and entry_path.name == deleted_folder_name:
                deleted_entries.append(entry)
            elif (
                entry_path.is_file()
                and entry_path.parent.name == deleted_folder_name
            ):
                deleted_entries.append(entry)

                # delete files
                entry_path.unlink()

        # ensure the above code is working correctly
        assert len(deleted_entries) == 5

        # delete folder
        deleted_folder_path.rmdir()

        differing_files = herkules_diff_run(
            original_paths,
            datafiles,
            relative_to_root=False,
            include_directories=True,
            directories_first=True,
        )

        assert differing_files['deleted'] == deleted_entries
        assert differing_files['added'] == []
        assert differing_files['modified'] == []

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_modify_file(
        self,
        datafiles,
    ):
        original_paths = herkules(
            datafiles,
            relative_to_root=True,
            add_metadata=True,
        )

        modified_path = datafiles / TEST_FILES[15]

        modified_entry = self.create_herkules_entry_from_path(
            modified_path,
            root_directory=datafiles,
        )

        # modify mtime
        modified_path.touch(exist_ok=True)

        differing_files = herkules_diff_run(
            original_paths,
            datafiles,
            relative_to_root=True,
        )

        assert differing_files['added'] == []
        assert differing_files['deleted'] == []

        first_entry = differing_files['modified'][0]
        assert first_entry['mtime_diff'] > 1e7

        # simplify test code
        del first_entry['mtime_diff']

        assert differing_files['modified'] == [
            modified_entry,
        ]
