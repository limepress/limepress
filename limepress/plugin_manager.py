from simple_plugin_manager import PluginManager


class LimepressPluginManager(PluginManager):
    HOOK_NAMES = [

        # setup hooks
        'pre_setup',
        'get_source_dirs',
        'get_template_dirs',
        'post_setup',

        # unit hooks
        'handle_unit_meta_data',
        'render_unit',
    ]
