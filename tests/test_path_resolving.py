def test_paths():
    from limepress.build_environment import LimepressBuildEnvironment

    build_env = LimepressBuildEnvironment()

    build_env.write_file('/src/test.html', """
        title: title


        ({{ path('/foo.html') }})
    """)

    build_env.build()

    # run test
    text = build_env.read_file('/build/test.html')

    assert '(foo.html)' in text


def test_stylesheets():
    from limepress.build_environment import LimepressBuildEnvironment

    build_env = LimepressBuildEnvironment()

    build_env.write_file('/src/test.html', """
        title: title


        {{ stylesheet('/static/foo.css') }}
    """)

    build_env.build()

    # run test
    text = build_env.read_file('/build/test.html')

    assert '<link href="static/foo.css" rel="stylesheet" />' in text


def test_scripts():
    from limepress.build_environment import LimepressBuildEnvironment

    build_env = LimepressBuildEnvironment()

    build_env.write_file('/src/test.html', """
        title: title


        {{ script('/static/foo.js') }}
    """)

    build_env.build()

    # run test
    text = build_env.read_file('/build/test.html')

    assert '<script src="static/foo.js"></script>' in text
