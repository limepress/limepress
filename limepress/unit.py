from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from loguru import logger
import os

from limepress.parsing import parse_unit_meta_data

if TYPE_CHECKING:  # pragma: no cover
    from limepress.context import LimepressContext


@dataclass
class LimepressUnit:

    # default attributes
    context: LimepressContext = field(repr=False)
    abs_path: str = field(default='')
    rel_path: str = field(default='')
    output_rel_path: str = field(default='')

    # templating
    template: str = field(default='')
    title: str = field(default='')
    body_title: str = field(default='')
    body_text: str = field(default='', repr=False)

    # meta data
    meta: dict = field(default_factory=dict, repr=False)

    # helper
    def is_disabled(self) -> bool:
        return not bool(self.output_rel_path)

    def is_template_unit(self) -> bool:
        return bool(self.template)

    def set_default_template(self) -> None:
        self.template = self.context.settings.DEFAULT_TEMPLATE

    def disable(self) -> None:
        self.output_rel_path = ''
        self.template = ''

    def get_file_extension(self) -> str:
        if not self.abs_path:
            return ''

        return os.path.splitext(self.abs_path)[1][1:].lower()

    def gen_rel_path(
            self,
            rel_path: str | None = None,
            output_rel_path: str | None = None,
            raise_exception: bool = False,
    ) -> str:

        # check arguments
        args = list(filter(None, [rel_path, output_rel_path]))

        if len(args) > 1:
            RuntimeError('to many arguments')

        elif len(args) < 1:
            RuntimeError('to few arguments')

        # check if output path is set
        if not self.output_rel_path:
            raise RuntimeError('unit has no output path')

        if rel_path:
            target_raw_path = rel_path

        elif output_rel_path:
            target_raw_path = output_rel_path

        # gen target_rel_path
        target_rel_path = target_raw_path

        if target_rel_path.startswith('./'):
            target_rel_path = target_rel_path[2:]

        if target_rel_path.startswith('/'):
            steps_up = len(
                list(filter(
                    None,
                    os.path.dirname(self.output_rel_path).split('/'),
                ))
            )

            target_rel_path = os.path.join(
                *(steps_up * ['../']),
                target_rel_path[1:],
            )

        # gen target_abs_path
        if target_raw_path.startswith('/'):
            target_abs_path = target_raw_path[1:]

        else:
            target_abs_path = os.path.join(
                os.path.dirname(self.output_rel_path),
                target_rel_path,
            )

        # resolve target unit to check if target path will be available
        target_unit: LimepressUnit | None = None

        def resolve_unit(rel_path, output_rel_path, target_abs_path):
            for unit in self.context.units:
                if rel_path and unit.rel_path == target_abs_path:
                    return unit

                if output_rel_path and unit.output_rel_path == target_abs_path:
                    return unit

            return None

        target_unit = resolve_unit(
            rel_path=rel_path,
            output_rel_path=output_rel_path,
            target_abs_path=target_abs_path,
        )

        # handling of index pages
        if not target_unit and not target_abs_path.endswith('index.html'):
            target_unit = resolve_unit(
                rel_path=rel_path,
                output_rel_path=output_rel_path,
                target_abs_path=os.path.join(target_abs_path, 'index.html'),
            )

        # log warning or raise exception if target unit was not found
        if not target_unit:
            if rel_path:
                warning_text = f'no unit with rel_path {rel_path} found'

            else:
                warning_text = f'no unit with output_rel_path {output_rel_path} found'  # NOQA

            if raise_exception:
                raise RuntimeError(warning_text)

            logger.warning(warning_text)

        return target_rel_path

    # parsing
    def load_meta_data(self) -> None:
        for key, value in parse_unit_meta_data(path=self.abs_path).items():
            self.meta[key] = value

        if 'title' in self.meta:
            self.title = self.meta['title']

        if 'template' in self.meta:
            self.template = self.meta['template']

        if 'output_rel_path' in self.meta:
            self.output_rel_path = self.meta['output_rel_path']

    def read_body(self) -> str:
        # TODO: return empty lines at the start to make error messages
        # of doctutils and markdown readable

        body_offset = self.meta.get('body_offset', 0)

        with open(self.abs_path, 'r') as f:
            for _ in range(body_offset):
                f.readline()

            return f.read()
