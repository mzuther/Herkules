import pathlib
from typing import TypedDict

Selector = dict[str, list[str]]
ModificationTime = float | None


class HerkulesEntry(TypedDict):
    path: pathlib.Path
    mtime: ModificationTime


class HerkulesEntryDiff(HerkulesEntry):
    mtime_diff: float


EntryList = list[HerkulesEntry]
EntryListFlattened = list[pathlib.Path]

EntryID = str
DictOfEntries = dict[EntryID, HerkulesEntry]


class DiffResult(TypedDict):
    added: list[HerkulesEntry]
    modified: list[HerkulesEntryDiff]
    deleted: list[HerkulesEntry]
