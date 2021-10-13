from os import nice
import pytest
from datetime import datetime as dt

import numpy as np
import pandas as pd

from dw_squared.client import DWSquared
from dw_squared.seasonal import Seasonal
from dw_squared.line import Lines
from dw_squared.area import Area
from dw_squared.bar import StackedBar


@pytest.fixture
def token(pytestconfig):
    return pytestconfig.getoption("token")


@pytest.fixture
def dw(token):
    return DWSquared(token)


def test_seasonal(token):
    range_date = pd.date_range(
        start=dt(2001, 1, 1), end=dt(2021, 9, 30), freq='D')
    data = pd.Series(np.cumsum(np.random.randn(len(range_date))),
                     index=range_date, name='serie')
    seasonal_plot = Seasonal(
        series=data,
        title='test_seasonal',
        token=token,
        source='me',
        notes='a note',
        prefix_unit='bananas',
        cutoff_year=2020,
    )
    seasonal_plot.publish()
    published = seasonal_plot.get_charts(search='test_seasonal', published=True)
    assert published[0]['id'] == seasonal_plot._chart['id']
    

def test_lines(token):
    range_date = pd.date_range(
        start=dt(2019, 1, 1), end=dt(2021, 9, 30), freq='D')
    data = pd.DataFrame(np.cumsum((np.random.randn(len(range_date), 5)), axis=0),
                        index=range_date, columns= [f'model_{i+1}' for i in range(5)])
    plot = Lines(
        frame=data,
        title='test_simple_line',
        token=token,
        source='me',
        notes='a note',
        prefix_unit='bananas',
        display_today=False
    )
    plot.publish()
    published = plot.get_charts(
        search='test_simple_line', published=True)
    assert published[0]['id'] == plot._chart['id']


def test_area(token):
    range_date = pd.date_range(
        start=dt(2019, 1, 1), end=dt(2021, 9, 30), freq='W')
    data = pd.DataFrame(
        data=np.cumsum(np.clip(np.random.randn(
            len(range_date), 2), a_min=0, a_max=None), axis=0),
        index=range_date, columns=['black_model', 'blue_model'])
    plot = Area(
        frame=data,
        title='test_simple_area',
        token=token,
        source='me',
        notes='a note',
        prefix_unit='bananas',
        display_today=False,
    )
    plot.publish()
    published = plot.get_charts(
        search='test_simple_area', published=True)
    assert published[0]['id'] == plot._chart['id']


def test_stacked_bar(token):
    range_date = pd.date_range(
        start=dt(2019, 1, 1), end=dt(2021, 9, 30), freq='Q')
    data = pd.DataFrame(
        data=np.cumsum(np.clip(np.random.randn(
            len(range_date), 2), a_min=0, a_max=None), axis=0),
        index=range_date, columns=['black_model', 'blue_model'])
    plot = StackedBar(
        frame=data,
        title='test_stacked',
        token=token,
        source='me',
        notes='a note',
        prefix_unit='bananas',
        display_today=False,
    )
    plot.publish()
    published = plot.get_charts(
        search='test_stacked', published=True)
    assert published[0]['id'] == plot._chart['id']
