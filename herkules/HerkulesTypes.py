import dataclasses
import pathlib
from typing import TypedDict, cast

Selector = dict[str, list[str]]
ModificationTime = float | None


class HerkulesEntryJSON(TypedDict):
    path: str
    mtime: float | None


class HerkulesEntryDiffJSON(HerkulesEntryJSON):
    mtime_diff: float


@dataclasses.dataclass
class HerkulesEntry:
    path: pathlib.Path
    mtime: ModificationTime

    def to_dict(
        self,
    ) -> HerkulesEntryJSON:
        return {
            # ensure stored JSON can be loaded correctly
            'path': str(self.path),
            'mtime': self.mtime,
        }


@dataclasses.dataclass
class HerkulesEntryDiff(HerkulesEntry):
    mtime_diff: float

    def to_entry(
        self,
    ) -> HerkulesEntry:
        return HerkulesEntry(
            path=self.path,
            mtime=self.mtime,
        )

    def to_dict(  # pragma: no coverage
        self,
    ) -> HerkulesEntryDiffJSON:
        # reuse code
        entry = cast(
            HerkulesEntryDiffJSON,
            super().to_dict(),
        )

        entry['mtime_diff'] = self.mtime_diff
        return entry


EntryList = list[HerkulesEntry]
EntryListJSON = list[HerkulesEntryJSON]
EntryListFlattened = list[pathlib.Path]

EntryID = str
DictOfEntries = dict[EntryID, HerkulesEntry]


class DiffResult(TypedDict):
    added: list[HerkulesEntry]
    modified: list[HerkulesEntryDiff]
    deleted: list[HerkulesEntry]
