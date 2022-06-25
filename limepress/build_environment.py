from tempfile import TemporaryDirectory
from typing import Tuple

from limepress.file_system import (
    make_directories as _make_directories,
    file_exists as _file_exists,
    write_file as _write_file,
    read_file as _read_file,
)

from limepress.context import LimepressContext
from limepress.settings import Settings


class LimepressBuildEnvironment:
    def __init__(self):
        self.tmp_dir: TemporaryDirectory = TemporaryDirectory()
        self.settings_overrides: Settings = Settings()
        self.context: LimepressContext | None = None

    # file handling ###########################################################
    def file_exists(self, path: str) -> bool:
        return _file_exists(
            root_dir=self.tmp_dir.name,
            path=path,
        )

    def make_directories(self, path: str) -> None:
        return _make_directories(
            root_dir=self.tmp_dir.name,
            path=path,
        )

    def read_file(self, path: str) -> str:
        return _read_file(
            root_dir=self.tmp_dir.name,
            path=path,
        )

    def write_file(self, path: str, text: str) -> Tuple[int]:
        return _write_file(
            root_dir=self.tmp_dir.name,
            path=path,
            text=text,
        )

    # setup ###################################################################
    def setup(self) -> None:
        self.context = LimepressContext(
            project_root=self.tmp_dir.name,
            settings_overrides=self.settings_overrides,
        )

    # helper ##################################################################
    def build(self) -> None:
        self.setup()

        assert self.context is not None

        self.context.build()
