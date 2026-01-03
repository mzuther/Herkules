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

import herkules.HerkulesTypes as Types
from herkules.Herkules import (
    herkules,
    herkules_diff,
    herkules_diff_run,
    herkules_with_metadata,
)
from tests.common import TEST_FILES, TestCommon

FIXTURE_DIR = pathlib.Path('tests') / 'beetle'


class TestHero(TestCommon):
    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_no_changes(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        original_paths = herkules_with_metadata(
            datafiles,
            relative_to_root=True,
        )

        # simulate loading original files from storage (paths as *strings*)
        original_paths_dict = [p.to_dict() for p in original_paths]

        original_files: Types.EntryListJSON = json.loads(
            json.dumps(
                original_paths_dict,
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
        correct_paths = herkules_with_metadata(
            datafiles,
        )

        no_paths: Types.EntryList = []

        with pytest.raises(
            ValueError,
            match=r'"original_entries" contains no entries',
        ):
            herkules_diff(
                original_entries_list=no_paths,
                actual_entries_list=correct_paths,
            )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_error_handling_no_entries_2(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        correct_paths = herkules_with_metadata(
            datafiles,
        )

        no_paths: Types.EntryList = []

        with pytest.raises(
            ValueError,
            match=r'"actual_entries" contains no entries',
        ):
            herkules_diff(
                original_entries_list=correct_paths,
                actual_entries_list=no_paths,
            )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_error_handling_no_metadata_1(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        correct_paths = herkules_with_metadata(
            datafiles,
        )

        flattened_paths = herkules(
            datafiles,
        )

        with pytest.raises(
            ValueError,
            match=r'"original_entries" has wrong type',
        ):
            herkules_diff(
                # type mismatch is test objective
                original_entries_list=flattened_paths,  # type: ignore
                actual_entries_list=correct_paths,
            )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_error_handling_no_metadata_2(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        correct_paths = herkules_with_metadata(
            datafiles,
        )

        flattened_paths = herkules(
            datafiles,
        )

        with pytest.raises(
            ValueError,
            match=r'"actual_entries" has wrong type',
        ):
            herkules_diff(
                original_entries_list=correct_paths,
                # type mismatch is test objective
                actual_entries_list=flattened_paths,  # type: ignore
            )

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_difference_no_changes_with_folders(
        self,
        datafiles: pathlib.Path,
    ) -> None:
        original_paths = herkules_with_metadata(
            datafiles,
            relative_to_root=True,
            include_directories=True,
            directories_first=True,
        )

        # simulate loading original files from storage (paths as *strings*)
        original_paths_dict = [p.to_dict() for p in original_paths]

        original_files: Types.EntryListJSON = json.loads(
            json.dumps(
                original_paths_dict,
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
        original_paths = herkules_with_metadata(
            datafiles,
            relative_to_root=True,
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
        original_paths = herkules_with_metadata(
            datafiles,
            relative_to_root=True,
            include_directories=True,
            directories_first=True,
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
        original_paths = herkules_with_metadata(
            datafiles,
            relative_to_root=True,
            include_directories=True,
            directories_first=False,
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

        actual_paths = herkules_with_metadata(
            datafiles,
            relative_to_root=True,
            include_directories=True,
            directories_first=True,
        )

        differing_files = herkules_diff(
            original_paths,
            actual_paths,
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
        original_paths = herkules_with_metadata(
            datafiles,
            relative_to_root=True,
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
        original_paths = herkules_with_metadata(
            datafiles,
            relative_to_root=True,
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
        original_paths = herkules_with_metadata(
            datafiles,
            relative_to_root=False,
            include_directories=True,
            directories_first=False,
        )

        deleted_folder_name = 'dir.ext'
        deleted_folder_path = datafiles / deleted_folder_name

        deleted_entries = []
        for entry in original_paths:
            if entry.path.is_dir() and entry.path.name == deleted_folder_name:
                deleted_entries.append(entry)
            elif (
                entry.path.is_file()
                and entry.path.parent.name == deleted_folder_name
            ):
                deleted_entries.append(entry)

                # delete files
                entry.path.unlink()

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
        original_paths = herkules_with_metadata(
            datafiles,
            relative_to_root=True,
        )

        modified_path = datafiles / TEST_FILES[15]

        # use current mtime
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

        # ensure "mtime_diff" is calculated correctly
        first_entry = differing_files['modified'][0]
        assert first_entry.mtime_diff > 0.0

        # ensure remainder of data is correct
        expected_paths = [modified_entry]

        modified_paths = [p.to_entry() for p in differing_files['modified']]

        assert modified_paths == expected_paths
