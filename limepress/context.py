from __future__ import annotations

from typing import Dict, List, Any
import os

from jinja2 import Environment, FileSystemLoader
from loguru import logger

from limepress.file_system import copy_files, write_file, clean_directory
from limepress.file_system import gen_limepress_src_path, iter_directory
from limepress.templating import LimepressSnippetTag, string_is_template
from limepress.dependency_manager import LimepressDependencyManager
from limepress.plugin_manager import LimepressPluginManager
from limepress.unit import LimepressUnit
from limepress.settings import Settings

DEFAULT_SETTINGS_PATHS = [
    gen_limepress_src_path('default_settings.py'),
]


class LimepressContext:
    # TODO: log exceptions

    def __init__(
            self,
            project_root: str,
            settings_paths: List[str] | None = None,
            settings_overrides: Settings | None = None,
            logger: Any = logger,
    ):

        # args
        self.project_root: str = project_root
        self.settings_paths: List[str] = settings_paths or []
        self.settings_overrides: Settings | None = settings_overrides
        self.logger = logger

        # state
        self.jinja2_env: Environment | None

        self.dependency_manager: LimepressDependencyManager = \
            LimepressDependencyManager(context=self)

        self.build_dir: str = ''
        self.source_dirs: List[str] = []
        self.template_dirs: List[str] = []
        self.units: List[LimepressUnit] = []

        # setup
        self.logger.debug('setup context')

        self._load_settings()
        self._load_plugins()
        self._run_pre_setup_hook()
        self._load_template_dirs()
        self._load_source_dirs()
        self._setup_build_dir()
        self._setup_templating_environment()
        self._run_post_setup_hook()
        self._run_checks()
        self._discover_units()

        self.logger.debug('setup done')

    def __repr__(self) -> str:
        return f'<LimepressContext(project_root={self.project_root!r})>'  # NOQA

    # setup ###################################################################
    def _load_settings(self) -> None:
        self.logger.debug('load settings')

        self.settings = Settings()

        self.settings_paths = [
            *DEFAULT_SETTINGS_PATHS,
            *(self.settings_paths or []),
        ]

        # check if project root contains a settings.py
        abs_path = self.gen_project_path('settings.py')

        if os.path.exists(abs_path):
            self.logger.debug('settings in project root discovered')

            self.settings_paths.append(abs_path)

        # load settings
        for settings_path in self.settings_paths:
            self.settings.add(settings_path)

        # overrides
        if self.settings_overrides:
            self.logger.debug('processing settings overrides')

            for key in self.settings_overrides:
                value = getattr(self.settings_overrides, key)

                setattr(self.settings, key, value)

    def _load_plugins(self) -> None:
        self.logger.debug('load plugins')

        self.plugin_manager = LimepressPluginManager()

        self.plugin_manager.load([
            *self.settings.DEFAULT_PLUGINS,
            *self.settings.PLUGINS,
        ])

    def _run_pre_setup_hook(self) -> None:
        self.plugin_manager.run_hook(
            hook_name='pre_setup',
            hook_args=[self],
        )

    def _load_template_dirs(self) -> None:
        self.logger.debug('load template dirs')

        self.template_dirs.clear()

        # get template dirs from settings
        for template_dir in [*self.settings.TEMPLATE_DIRS,
                             *self.settings.DEFAULT_TEMPLATE_DIRS]:

            self.template_dirs.append(str(template_dir))

        # get template dirs from plugins
        return_values = self.plugin_manager.run_hook(
            hook_name='get_template_dirs',
            hook_args=[self],
        )

        for return_value in return_values:
            self.template_dirs.extend(return_value)

        # search for settings in project root
        abs_paths = self.gen_project_path('templates')

        if os.path.exists(abs_paths):
            self.logger.debug('template dir in project root discovered')

            self.template_dirs.insert(0, abs_paths)

        self.logger.debug('loaded template dirs: {}', self.template_dirs)

    def _load_source_dirs(self) -> None:
        self.logger.debug('load source dirs')

        self.source_dirs.clear()

        # get source dirs from settings
        for source_dir in self.settings.SOURCE_DIRS:
            self.source_dirs.append(str(source_dir))

        # get source dirs from plugins
        return_values = self.plugin_manager.run_hook(
            hook_name='get_source_dirs',
            hook_args=[self],
        )

        for return_value in return_values:
            self.source_dirs.extend(return_value)

        # search for source dir in project root
        abs_paths = self.gen_project_path('src')

        if os.path.exists(abs_paths):
            self.logger.debug('source dir in project root discovered')

            self.source_dirs.append(abs_paths)

        self.logger.debug('loaded source dirs: {}', self.source_dirs)

    def _setup_build_dir(self) -> None:
        self.logger.debug('setup build dir')

        self.build_dir = self.gen_project_path(
            path=self.settings.BUILD_DIR,
        )

        self.logger.debug('build dir is set to {}', self.build_dir)

    def _setup_templating_environment(self) -> None:
        self.logger.debug('setup templating environment')

        # setup jinja2 environment
        self.jinja2_env = Environment(
            loader=FileSystemLoader(
                searchpath=self.template_dirs,
                followlinks=True,
            ),
        )

        # setup snippet extension
        self.jinja2_env.add_extension(LimepressSnippetTag)

    def _run_post_setup_hook(self) -> None:
        self.plugin_manager.run_hook(
            hook_name='post_setup',
            hook_args=[self],
        )

    def _discover_units(self) -> None:
        self.logger.debug('discover units')

        for raw_source_dir in self.source_dirs:
            source_dir = self.gen_project_path(raw_source_dir)

            self.logger.debug('scanning {}', source_dir)

            for abs_path, rel_path in iter_directory(source_dir):
                self.logger.debug('processing {}', abs_path)

                # setup unit
                unit = self.gen_unit()

                unit.abs_path = abs_path
                unit.rel_path = rel_path
                unit.output_rel_path = rel_path

                # run plugin chain
                self.plugin_manager.run_hook(
                    hook_name='handle_unit_meta_data',
                    hook_args=[unit],
                )

    def _run_checks(self) -> None:
        # TODO

        pass

    # templating ##############################################################
    def gen_template_context(self, overrides: Dict[Any, Any] | None) -> dict:
        return {
            **self.settings.DEFAULT_TEMPLATE_CONTEXT,
            **self.settings.TEMPLATE_CONTEXT,
            **{
                'context': self,
            },
            **(overrides or {}),
        }

    def render_template(
            self,
            name: str,
            context: Dict[Any, Any] | None,
    ) -> str:

        if not self.jinja2_env:
            raise RuntimeError('templating environment is not setup')

        template = self.jinja2_env.get_template(name=name)
        context = self.gen_template_context(overrides=context)

        return template.render(**context)

    def render_template_string(
            self,
            string: str,
            context: Dict[Any, Any] | None,
    ) -> str:

        if not self.jinja2_env:
            raise RuntimeError('templating environment is not setup')

        template = self.jinja2_env.from_string(source=string)
        context = self.gen_template_context(overrides=context)

        return template.render(**context)

    # path helper #############################################################
    def gen_project_path(self, path: str) -> str:
        if path.startswith('/'):
            return path

        return os.path.join(
            self.project_root,
            path,
        )

    def gen_output_path(self, path: str) -> str:
        if path.startswith('/'):
            path = path[1:]

        return os.path.join(
            self.build_dir,
            path,
        )

    # units ###################################################################
    def gen_unit(self) -> LimepressUnit:
        unit: LimepressUnit = LimepressUnit(context=self)

        self.units.append(unit)

        return unit

    # build ###################################################################
    def _clean_build_dir(self):
        self.logger.info('cleaning build dir')

        if os.path.exists(self.build_dir):
            clean_directory(self.build_dir)

    def _render_template_unit(self, unit: LimepressUnit) -> None:

        # run plugin hook 'render_unit'
        self.plugin_manager.run_hook(
            hook_name='render_unit',
            hook_kwargs={
                'unit': unit,
            },
        )

        # setup template context
        template_context = self.gen_template_context({
            'unit': unit,
            'title': unit.title,
            'body_title': unit.body_title,
            'body_text': unit.body_text,
        })

        # pre render title
        if(unit.meta.get('title_is_template', True) and
           string_is_template(template_context['title'])):

            template_context['title'] = self.render_template_string(
                string=template_context['title'],
                context={
                    'unit': unit,
                },
            )

        # pre render body_title
        if(unit.meta.get('body_title_is_template', True) and
           string_is_template(template_context['body_title'])):

            template_context['body_title'] = self.render_template_string(
                string=template_context['body_title'],
                context={
                    'unit': unit,
                },
            )

        # pre render body_text
        if(unit.meta.get('body_text_is_template', True) and
           string_is_template(template_context['body_text'])):

            template_context['body_text'] = self.render_template_string(
                string=template_context['body_text'],
                context={
                    'unit': unit,
                },
            )

        # render unit and write to output path
        text = self.render_template(
            name=unit.template,
            context=template_context,
        )

        write_file(
            root_dir='/',  # FIXME
            path=self.gen_output_path(path=unit.output_rel_path),
            text=text,
        )

        # discard unit.body_text to save memory
        unit.body_text = ''

    def _render_units(self) -> List[LimepressUnit]:
        self.logger.debug('rendering units')

        rendered_units: List[LimepressUnit] = []
        exception_raised: bool = False

        for unit in self.units:
            self.logger.debug('rendering {}', unit)

            if unit.is_disabled():
                self.logger.debug('{} is disabled', unit)

                continue

            try:

                # template units
                if unit.is_template_unit():
                    self._render_template_unit(unit=unit)

                # file units
                else:
                    copy_files(
                        source=unit.abs_path,
                        destination=self.gen_output_path(
                            path=unit.output_rel_path,
                        ),
                    )

                rendered_units.append(unit)

            except Exception:
                exception_raised = True

                self.logger.exception(
                    'exception raised while rendering {}',
                    unit,
                )

        if len(rendered_units) == 0 and not exception_raised:
            self.logger.info('nothing to do')

        return rendered_units

    def build(self, clean: bool = False) -> List[LimepressUnit]:
        self.logger.debug('start build')

        if clean:
            self._clean_build_dir()

        else:
            self.dependency_manager.disable_unchanged_units()

        rendered_units = self._render_units()

        self.logger.debug('build done')

        return rendered_units
