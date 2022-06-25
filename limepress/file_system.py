from typing import Iterator, Tuple
import shutil
import os

from loguru import logger

import limepress

LIMEPRESS_ROOT = os.path.dirname(limepress.__file__)


def gen_limepress_src_path(path: str) -> str:
    if path.startswith('/'):
        path = path[1:]

    return os.path.join(LIMEPRESS_ROOT, path)


def _gen_abs_path(root_dir: str, path: str) -> str:
    if path.startswith('/'):
        path = path[1:]

    return os.path.join(root_dir, path)


def file_exists(
        root_dir: str,
        path: str,
) -> bool:

    abs_path = _gen_abs_path(
        root_dir=root_dir,
        path=path,
    )

    return os.path.exists(abs_path)


def make_directories(
        root_dir: str,
        path: str,
) -> None:

    abs_path = _gen_abs_path(
        root_dir=root_dir,
        path=path,
    )

    if os.path.exists(abs_path):
        return

    logger.debug('making directories {}', abs_path)

    os.makedirs(abs_path)


def read_file(
        root_dir: str,
        path: str,
        mode: str = 'r',
) -> str:

    abs_path = _gen_abs_path(
        root_dir=root_dir,
        path=path,
    )

    logger.debug('reading file {} (mode={})', abs_path, mode)

    return str(open(abs_path, mode=mode).read())


def write_file(
        root_dir: str,
        path: str,
        text: str,
        mode: str = 'w+',
) -> Tuple[int]:

    abs_path = _gen_abs_path(
        root_dir=root_dir,
        path=path,
    )

    make_directories(
        root_dir=root_dir,
        path=os.path.dirname(path),
    )

    logger.info('writing file {} (mode={})', abs_path, mode)

    return open(abs_path, mode=mode).write(text),


def copy_files(
        source: str,
        destination: str,
) -> None:

    destination_dirname = os.path.dirname(destination)

    logger.info('copying {} to {}', source, destination)

    if not os.path.exists(destination_dirname):
        os.makedirs(destination_dirname)

    shutil.copy(src=source, dst=destination)


def iter_directory(
        root_dir: str,
) -> Iterator[Tuple[str, str]]:

    for root, _, files in os.walk(root_dir):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, root_dir)

            yield abs_path, rel_path


def clean_directory(path: str) -> None:
    logger.debug('cleaning directory {}', path)

    if not os.path.exists(path):
        raise RuntimeError('{} does not exist', path)

    if not os.path.isdir(path):
        raise RuntimeError('{} is no directory', path)

    for rel_directory_entry in os.listdir(path):
        abs_directory_entry = os.path.join(path, rel_directory_entry)

        logger.debug('removing {}', abs_directory_entry)

        if os.path.isdir(abs_directory_entry):
            shutil.rmtree(abs_directory_entry)

        else:
            os.unlink(abs_directory_entry)
