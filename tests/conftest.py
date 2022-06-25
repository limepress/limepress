import os

import pytest

TEST_FILE_ROOT = os.path.join(
    os.path.dirname(__file__),
    'test-files',
)


@pytest.fixture
def get_test_file_path():
    def _get_test_file_path(name):
        test_file_path = os.path.join(
            TEST_FILE_ROOT,
            name,
        )

        assert os.path.exists(test_file_path)

        return test_file_path

    return _get_test_file_path
