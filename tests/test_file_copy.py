def test_copy():
    from limepress.build_environment import LimepressBuildEnvironment

    build_env = LimepressBuildEnvironment()

    build_env.write_file('/src/foo.txt', 'foo')
    build_env.write_file('/src/foo/bar.txt', 'bar')
    build_env.write_file('/src/foo/bar/baz.txt', 'baz')

    build_env.build()

    # run test
    assert build_env.read_file('/build/foo.txt') == 'foo'
    assert build_env.read_file('/build/foo/bar.txt') == 'bar'
    assert build_env.read_file('/build/foo/bar/baz.txt') == 'baz'


def test_multiple_source_dirs():
    from limepress.build_environment import LimepressBuildEnvironment

    build_env = LimepressBuildEnvironment()

    build_env.settings_overrides.SOURCE_DIRS = [
        'src1',
        'src2',
    ]

    # src1
    build_env.write_file('/src1/foo.txt', 'foo1')
    build_env.write_file('/src1/bar.txt', 'bar')

    # src2
    build_env.write_file('/src2/foo.txt', 'foo2')
    build_env.write_file('/src2/baz.txt', 'baz')

    # build
    build_env.build()

    # run tests
    assert build_env.read_file('/build/foo.txt') == 'foo2'
    assert build_env.read_file('/build/bar.txt') == 'bar'
    assert build_env.read_file('/build/baz.txt') == 'baz'


def test_custom_source_file_handling():
    from limepress.build_environment import LimepressBuildEnvironment

    # setup environment
    handled_units = []

    class TestPlugin:
        handled_files = []

        def unit_discovered(self, unit):
            if not unit.rel_path.endswith('.test'):
                return unit

            unit.disabled = True

            handled_units.append(unit.rel_path)

    build_env = LimepressBuildEnvironment()

    build_env.settings_overrides.PLUGINS = [
        TestPlugin,
    ]

    # setup src files
    build_env.write_file('/src/foo.txt', 'foo')
    build_env.write_file('/src/foo.test', 'test')

    # run test
    build_env.build()

    assert build_env.file_exists('/build/foo.txt')
    assert not build_env.file_exists('/build/foo.test')
    assert handled_units == ['foo.test']
