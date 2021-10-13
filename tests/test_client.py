import pytest
from datetime import datetime as dt

import numpy as np
import pandas as pd

from dw_squared.client import DWSquared, Seasonal


@pytest.fixture
def token(pytestconfig):
    return pytestconfig.getoption("token")


@pytest.fixture
def dw(token):
    return DWSquared(token)


def test_dwsquared_ping(dw):
    info = dw.dw.account_info()
    assert [x in list(info.keys()) for x in ('email', 'id')]


def test_seasonal(token):
    range_date = pd.date_range(
        start=dt(2001, 1, 1), end=dt(2021, 9, 30), freq='D')
    data = pd.Series(np.cumsum(np.random.randn(len(range_date))),
                     index=range_date, name='serie')
    seasonal_plot = Seasonal(
        series=data,
        title='test',
        token=token,
        source='me',
        notes='a note',
        prefix_unit='bananas',
        cutoff_year=2020,
    )
    seasonal_plot.publish()
    published = seasonal_plot.get_charts(search='test', published=True)
    assert published[0]['id'] == seasonal_plot._chart['id']
