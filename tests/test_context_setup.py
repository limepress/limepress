def test_empty_project_root():
    from limepress.build_environment import LimepressBuildEnvironment
    from limepress.file_system import gen_limepress_src_path

    build_env = LimepressBuildEnvironment()
    build_env.setup()

    assert build_env.context.source_dirs == []

    assert build_env.context.template_dirs == [
        gen_limepress_src_path('/templates'),
    ]


def test_settings_discovery():
    from limepress.build_environment import LimepressBuildEnvironment

    # without user settings
    build_env = LimepressBuildEnvironment()
    build_env.setup()

    assert not hasattr(build_env.context.settings, 'FOO')

    # with user settings
    build_env = LimepressBuildEnvironment()

    build_env.write_file('settings.py', "FOO = 'bar'")

    build_env.setup()

    assert getattr(build_env.context.settings, 'FOO') == 'bar'


def test_source_dir_discovery():
    import os

    from limepress.build_environment import LimepressBuildEnvironment

    build_env = LimepressBuildEnvironment()

    build_env.make_directories('/src')
    build_env.setup()

    assert build_env.context.source_dirs == [
        os.path.join(
            build_env.tmp_dir.name,
            'src',
        ),
    ]


def test_template_dir_discovery():
    import os

    from limepress.build_environment import LimepressBuildEnvironment
    from limepress.file_system import gen_limepress_src_path

    build_env = LimepressBuildEnvironment()

    build_env.make_directories('/templates')
    build_env.setup()

    assert build_env.context.template_dirs == [
        os.path.join(
            build_env.tmp_dir.name,
            'templates',
        ),
        gen_limepress_src_path('/templates'),
    ]
