import pytest

from dw_squared.client import DWSquared


@pytest.fixture
def token(pytestconfig):
    return pytestconfig.getoption("token")


@pytest.fixture
def dw(token):
    return DWSquared(token)


def test_dwsquared_ping(dw):
    info = dw.dw.account_info()
    assert [x in list(info.keys()) for x in ('email', 'id')]


def test_dwsquared_search(dw):
    charts = dw.get_charts(published=False)
    for ch in charts:
        print(ch)
    assert False
