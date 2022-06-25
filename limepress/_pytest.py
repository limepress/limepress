import pytest

from limepress._logging import setup_propagate_handler


@pytest.fixture(autouse=True, scope='session')
def limepress_setup_for_testing() -> None:
    setup_propagate_handler()
