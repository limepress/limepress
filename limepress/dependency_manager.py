from typing import TYPE_CHECKING
import pathlib
import os

if TYPE_CHECKING:  # pragma: no cover
    from limepress.context import LimepressContext


class LimepressDependencyManager:
    # TODO: add handling of unit.meta['depends']

    def __init__(self, context: 'LimepressContext'):
        self.context = context

    def get_mtime(self, path: str) -> float:
        return pathlib.Path(path).stat().st_mtime

    def get_last_modified_template_mtime(self) -> float:
        if not self.context.jinja2_env:
            raise RuntimeError('templating environment is not setup')

        mtime = 0.0

        for template_name in self.context.jinja2_env.list_templates():
            if self.context.path_is_ignored(template_name)[0]:
                continue

            template = self.context.jinja2_env.get_template(template_name)
            template_mtime = self.get_mtime(str(template.filename))

            if template_mtime > mtime:
                mtime = template_mtime

        return mtime

    def get_last_modified_settings_mtime(self) -> float:
        mtime = 0.0

        for settings_path in self.context.settings_paths:
            if self.context.path_is_ignored(settings_path)[0]:
                continue

            settings_mtime = self.get_mtime(settings_path)

            if settings_mtime > mtime:
                mtime = settings_mtime

        return mtime

    def set_unchanged_units_not_dirty(self) -> None:
        last_modified_template_mtime = self.get_last_modified_template_mtime()
        last_modified_settings_mtime = self.get_last_modified_settings_mtime()

        for unit in self.context.units:

            # skip previously disabled units
            if unit.disabled:
                continue

            # skip non dirty units
            if not unit.dirty:
                continue

            # skip units that have no path
            if not unit.abs_path:
                continue

            # skip units that were never written before
            output_path = self.context.gen_output_path(
                path=unit.output_rel_path,
            )

            if not os.path.exists(output_path):
                continue

            # check if templates or settings changed
            dst_mtime = self.get_mtime(output_path)

            if last_modified_settings_mtime > dst_mtime:
                continue

            if unit.template:
                if last_modified_template_mtime > dst_mtime:
                    continue

            # check if source file is newer than destination file
            src_mtime = self.get_mtime(unit.abs_path)

            if src_mtime < dst_mtime:
                unit.dirty = False
