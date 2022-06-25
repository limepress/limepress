def test_simple_unit(get_test_file_path):
    from limepress.parsing import parse_unit_meta_data

    file_path = get_test_file_path('simple-unit.html')
    meta_data = parse_unit_meta_data(file_path)

    # default keys
    assert meta_data['body_offset'] == 5

    # meta data
    assert meta_data['a'] == 1
    assert meta_data['b'] == 'foo'
    assert meta_data['c'] == ['a', 'b', 'c']


def test_unit_with_multiple_empty_lines(get_test_file_path):
    from limepress.parsing import parse_unit_meta_data

    file_path = get_test_file_path('unit-with-multiple-empty-lines.html')
    meta_data = parse_unit_meta_data(file_path)

    # default keys
    assert meta_data['body_offset'] == 7

    # meta data
    assert meta_data['a'] == 1
    assert meta_data['b'] == 'foo'
    assert meta_data['c'] == ['a', 'b', 'c']


def test_unit_without_meta_data(get_test_file_path):
    from limepress.parsing import parse_unit_meta_data

    file_path = get_test_file_path('unit-without-meta-data.html')
    meta_data = parse_unit_meta_data(file_path)

    # default keys
    assert len(list(meta_data.keys()))
    assert meta_data['body_offset'] == 0


def test_unit_parsing_api(get_test_file_path):
    from limepress.unit import LimepressUnit

    # setup
    unit = LimepressUnit(context=None)

    unit.abs_path = get_test_file_path('simple-unit.html')

    # meta data
    unit.load_meta_data()

    assert unit.meta['body_offset'] == 5
    assert unit.meta['a'] == 1
    assert unit.meta['b'] == 'foo'
    assert unit.meta['c'] == ['a', 'b', 'c']

    # body
    body = unit.read_body()

    assert body.strip() == '<h1>Hello World</h1>\n<p>Lorem Ipsum</p>'
