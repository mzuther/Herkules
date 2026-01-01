# The story, all names, characters, and incidents portrayed in this test are
# fictitious. No identification with actual persons (living or deceased),
# places, buildings, and products is intended or should be inferred.
#
# In other words: I have great and helpful colleagues with a lot of humour. In
# order to make writing these tests more fun, I have used their (obfuscated)
# names, but all personality traits have been made up. I hope they have as much
# fun reading these tests as I had in writing them!

import json
import pathlib

import pytest

from herkules.Herkules import herkules, herkules_diff, herkules_diff_run
from tests.common import TEST_FILES, TestCommon

FIXTURE_DIR = pathlib.Path('tests') / 'beetle'


class TestBeetle(TestCommon):
    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_no_changes(
        self,
        datafiles: pathlib.Path,
    ) -> None:
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
        datafiles: pathlib.Path,
    ) -> None:
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
            exc_info.value.args[0] == '"original_entries" contains no entries'
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_error_handling_no_entries_2(
        self,
        datafiles: pathlib.Path,
    ) -> None:
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

        assert exc_info.value.args[0] == '"actual_entries" contains no entries'

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_error_handling_no_metadata_1(
        self,
        datafiles: pathlib.Path,
    ) -> None:
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
            exc_info.value.args[0] == '"original_entries" contains no metadata'
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_error_handling_no_metadata_2(
        self,
        datafiles: pathlib.Path,
    ) -> None:
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
            exc_info.value.args[0] == '"actual_entries" contains no metadata'
        )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_no_changes_with_folders(
        self,
        datafiles: pathlib.Path,
    ) -> None:
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
        datafiles: pathlib.Path,
    ) -> None:
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
        datafiles: pathlib.Path,
    ) -> None:
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
        datafiles: pathlib.Path,
    ) -> None:
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
        datafiles: pathlib.Path,
    ) -> None:
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
        datafiles: pathlib.Path,
    ) -> None:
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
        datafiles: pathlib.Path,
    ) -> None:
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
        datafiles: pathlib.Path,
    ) -> None:
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
