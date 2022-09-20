from typing import Dict, List, Any

from limepress.templating import stylesheet, script, path
from limepress.file_system import gen_limepress_src_path

# build
SOURCE_DIRS: List[str] = []
BUILD_DIR: str = 'build'

# plugins
DEFAULT_PLUGINS: List[str] = [
    gen_limepress_src_path('plugins/html_parser.py::LimepressHtmlParser'),
]

PLUGINS: List[Any] = []

# templating
DEFAULT_TEMPLATE_DIRS: List[str] = [
    gen_limepress_src_path('templates')
]

TEMPLATE_DIRS: List[str] = []
DEFAULT_TEMPLATE: str = 'page.html'

DEFAULT_TEMPLATE_CONTEXT: Dict[str, Any] = {
    'stylesheet': stylesheet,
    'script': script,
    'path': path,
}

TEMPLATE_CONTEXT: Dict[str, Any] = {}

# links
SHORT_INDEX_LINKS: bool = True
APPEND_SLASH: bool = True

# units
DEFAULT_IGNORE: List[str] = [
    '~*',
    '*.swp',
    '*.tmp',
]

IGNORE: List[str] = []
