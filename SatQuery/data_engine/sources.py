"""Input source abstractions for the SatQuery Data Engine."""
from dataclasses import dataclass
from pathlib import Path
from typing import Union

PathLike = Union[str, Path]

@dataclass(frozen=True)
class LocalFileSource:
    path: Path

    def __init__(self, path: PathLike):
        object.__setattr__(self, "path", Path(path).expanduser())

    @property
    def display_name(self) -> str:
        return self.path.name
