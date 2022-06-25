# TODO: add snippets without body

from __future__ import annotations

from typing import Callable, Dict, Any
import textwrap
import os
import re

from jinja2_simple_tags import ContainerTag
from jinja2 import pass_context
from loguru import logger

from limepress.unit import LimepressUnit


def string_is_template(string: str) -> bool:
    return '{{' in string or '{%' in string


@pass_context
def path(
        context: dict,
        rel_path: str | None = None,
        output_rel_path: str | None = None,
) -> str:

    unit: LimepressUnit = context['unit']

    return unit.gen_rel_path(
        rel_path=rel_path,
        output_rel_path=output_rel_path,
    )


@pass_context
def stylesheet(
        context: dict,
        href: str,
        **kwargs: Dict[str, str],
) -> str:

    unit: LimepressUnit = context['unit']

    link_kwargs: Dict[str, str] = {
        'href': unit.gen_rel_path(output_rel_path=href),
        'rel': 'stylesheet',
    }

    # FIXME
    link_kwargs.update(kwargs)  # type: ignore

    link_kwargs_string: str = ' '.join(
        [f'{key}="{value}"' for key, value in link_kwargs.items()]
    )

    return f'<link {link_kwargs_string} />'


@pass_context
def script(
        context: dict,
        href: str,
        **kwargs: Dict[str, str],
) -> str:

    unit: LimepressUnit = context['unit']

    script_kwargs: Dict[str, str] = {
        'href': unit.gen_rel_path(output_rel_path=href),
    }

    # FIXME
    script_kwargs.update(kwargs)  # type: ignore

    script_kwargs_string: str = ' '.join(
        [f'{key}="{value}"' for key, value in script_kwargs.items()]
    )

    return f'<script {script_kwargs_string}></script>'


class LimepressSnippetTag(ContainerTag):
    SNIPPET_NAME_RE = re.compile(r'^[0-9a-zA-Z_-]+$')

    def __init__(self, environment):
        super().__init__(environment)

        self._discover_snippets()

    def _discover_snippets(self):
        """
        snippet name format: 'snippet/[SNIPPET_NAME](.[EXTENSION])'
        """

        self.tags = []
        self.snippets = {}

        for template_name in self.environment.list_templates():
            path_parts = template_name.split('/')

            if len(path_parts) != 2:
                continue

            if path_parts[-2] != 'snippets':
                continue

            snippet_raw_name = path_parts[-1]

            # remove extension
            snippet_name, _ = os.path.splitext(snippet_raw_name)

            # check if snippet name is valid
            if not self.SNIPPET_NAME_RE.match(snippet_name):
                logger.warning('invalid snippet name: {}', template_name)

                continue

            # register snippet
            self.tags.append(snippet_name)
            self.snippets[snippet_name] = template_name

        logger.debug('discovered snippets: {}', self.tags)

    def render(
            self,
            caller: Callable,
            dedent_text: bool = True,
            **kwargs: Dict[Any, Any],
    ) -> str:

        # generate snippet text
        snippet_text = caller()

        if dedent_text:
            snippet_text = textwrap.dedent(snippet_text).strip()

        # generate template context
        template_context = {
            **self.context,
            'snippet': {
                'dedent_text': dedent_text,
                'text': snippet_text,
                **kwargs,
            },
        }

        # render snippet template
        template_path = self.snippets[self.tag_name]
        template = self.environment.get_template(template_path)

        return str(template.render(**template_context))
