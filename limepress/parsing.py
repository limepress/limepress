from __future__ import annotations

from typing import Dict, Any
import re

from yaml import safe_load

NO_META_DATA_RE = re.compile(r'^((\s+)?\n){2,}')
DELIMITER_RE = re.compile(r'((\s+)?\n){3,}')


class ParsingError(Exception):
    pass


class NoDelimiterFoundError(ParsingError):
    pass


class InvalidMetaDataError(ParsingError):
    pass


class InvalidMetaDataFormatError(ParsingError):
    pass


def parse_unit_meta_data(path: str) -> Dict[str, Any]:
    meta_data = {
        'body_offset': 0,
    }

    file_content = open(path, 'r').read()

    # unit without meta data
    match = NO_META_DATA_RE.search(file_content)

    if match:
        meta_data['body_offset'] = 0

        return meta_data

    # find delimiter
    match = DELIMITER_RE.search(file_content)

    if not match:
        raise NoDelimiterFoundError()

    # split body
    delimiter_start, delimiter_end = match.span()

    delimiter = file_content[delimiter_start:delimiter_end]
    meta_data_string = file_content[:delimiter_start]

    meta_data['body_offset'] = (len(meta_data_string.splitlines()) +
                                len(delimiter.splitlines()) - 1)

    # parse meta data
    try:
        yaml_data = safe_load(meta_data_string)

    except Exception:
        raise InvalidMetaDataError()

    if not isinstance(yaml_data, dict):
        raise InvalidMetaDataFormatError()

    for key, value in yaml_data.items():
        meta_data[key] = value

    return meta_data
