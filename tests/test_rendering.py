def test_basic_rendering():
    from limepress.build_environment import LimepressBuildEnvironment

    build_env = LimepressBuildEnvironment()

    build_env.write_file('/src/test.html', """
        title: title


        <h1>Hello World</h1>'
    """)

    build_env.write_file('/src/test-dir/test.html', """
        title: title


        <h1>Hello World2</h1>,
    """)

    build_env.build()

    # run test
    text = build_env.read_file('/build/test.html')

    assert '<html' in text
    assert '<body' in text
    assert '<h1>Hello World</h1>' in text

    text = build_env.read_file('/build/test-dir/test.html')

    assert '<html' in text
    assert '<body' in text
    assert '<h1>Hello World2</h1>' in text


def test_title_pre_rendering():
    from limepress.build_environment import LimepressBuildEnvironment

    build_env = LimepressBuildEnvironment()

    build_env.write_file('/src/test.html', """
        title: "{{ 'fo' + 'o' }}"


        <h1>Hello World</h1>
    """)

    build_env.build()

    # run test
    text = build_env.read_file('/build/test.html')

    assert '<title>foo</title>' in text

def test_body_title_pre_rendering():
    from limepress.build_environment import LimepressBuildEnvironment

    build_env = LimepressBuildEnvironment()

    build_env.write_file('/src/test.html', """
        title: title


        <h1>Hello {{ 1 + 1 }} World</h1>
    """)

    build_env.build()

    # run test
    text = build_env.read_file('/build/test.html')

    assert '<h1>Hello 2 World</h1>' in text


def test_body_text_pre_rendering():
    from limepress.build_environment import LimepressBuildEnvironment

    build_env = LimepressBuildEnvironment()

    build_env.write_file('/src/test.html', """
        title: title


        <div>Hello {{ 1 + 1 }} World</div>
    """)

    build_env.build()

    # run test
    text = build_env.read_file('/build/test.html')

    assert '<div>Hello 2 World</div>' in text


def test_snippets():
    from limepress.build_environment import LimepressBuildEnvironment

    build_env = LimepressBuildEnvironment()

    build_env.write_file('/src/test.html', """
        title: title


        {% pre %}
            foo
        {% endpre %}
    """)

    build_env.build()

    # run test
    text = build_env.read_file('/build/test.html')

    assert '<pre>foo</pre>' in text


def test_generated_unit():
    from limepress.build_environment import LimepressBuildEnvironment

    # setup build environment
    build_env = LimepressBuildEnvironment()

    build_env.setup()

    # generate unit
    unit = build_env.context.gen_unit()

    unit.output_rel_path = 'test.txt'
    unit.text = 'Hello World'

    # build
    build_env.build()

    # run test
    text = build_env.read_file('/build/test.txt')

    assert text == 'Hello World'
