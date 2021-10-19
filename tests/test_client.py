import pytest
from tshistory.api import timeseries

from dw_squared.client import (PlotConfig, TableConfig, create_single_plot,
                               create_single_table, get_data, saturn_to_frame, update_single_plot)


@pytest.fixture
def token(pytestconfig):
    return pytestconfig.getoption("token")


@pytest.fixture
def endpoint(pytestconfig):
    return pytestconfig.getoption("endpoint")


@pytest.fixture
def mapping(pytestconfig):
    return pytestconfig.getoption("mapping")


def test_plot_config():
    plotconfig = PlotConfig('tests/mapping.yaml')
    assert len(plotconfig.config) == 2


def test_plot(token, endpoint, mapping):
    plotconfig = PlotConfig(mapping)
    title = plotconfig.config[0]['title']
    tsa = timeseries(endpoint)
    program = plotconfig.series_bounds([title])
    data = get_data(tsa, program)
    data = saturn_to_frame(data, plotconfig, title)
    create_single_plot(data, plotconfig, title, token)

def test_table(token, endpoint, mapping):
    tableconfig = TableConfig(mapping)
    title = tableconfig.config[1]['title']
    tsa = timeseries(endpoint)
    program = tableconfig.series_bounds([title])
    data = get_data(tsa, program)
    data = saturn_to_frame(data, tableconfig, title)
    create_single_table(data, tableconfig, title, token)
