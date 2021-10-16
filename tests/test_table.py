import pytest
from datetime import datetime as dt

import pandas as pd
import numpy as np

from dw_squared.table import Table, triple_loop_dict, triple_loop_list, within_key


@pytest.fixture
def token(pytestconfig):
    return pytestconfig.getoption("token")


@pytest.fixture
def table_config():
    return {'L1': [
        {'key': 'level_l1_0',
         'value': 'a',
         'L2': [
             {'key': 'level_l1_l2_0',
              'value': 'b',
              'L3': [{'key': 'level_l1_l2_l3_0',
                      'value': 'b'}]},
             {'key': 'level_l1_l2_1',
                 'value': 'c'}
         ]},
        {'key': 'level_l1_1',
         'value': 'd'}
    ]}


def test_triple_loop_dict(table_config):
    data = triple_loop_dict(table_config, 'key', 'value')
    assert data == {'level_l1_0': 'a', 'level_l1_1': 'd',
                    'level_l1_l2_0': 'b', 'level_l1_l2_1': 'c',
                    'level_l1_l2_l3_0': 'b'}


def test_triple_loop_list(table_config):
    data = triple_loop_list(table_config, 'key')
    assert data == ['level_l1_0', 'level_l1_l2_0',
                    'level_l1_l2_l3_0', 'level_l1_l2_1',
                    'level_l1_1']


def test_within_key(table_config):
    data = within_key(table_config, 'key')
    assert data == {'L1': ['level_l1_0', 'level_l1_1'],
                    'L2': ['level_l1_l2_0', 'level_l1_l2_1'],
                    'L3': ['level_l1_l2_l3_0']}


def test_freq_agg(token):
    range_date = pd.date_range(
        start=dt(2021, 1, 1), end=dt(2024, 9, 30), freq='M')
    data = pd.DataFrame(
        data=np.cumsum(np.random.randn(
            len(range_date), 4), axis=0),
        index=range_date, 
        columns=['level_l1_0', 'level_l1_1', 
        'level_l1_l2_0', 'level_l1_l2_l3_0'])

    table_config = {'L1': [
        {'legend': 'level_l1_0',
         'aggregation_freq': 'mean',
         'aggregation_level': 'sum',
         'L2': [
             {'legend': 'level_l1_l2_0',
              'aggregation_freq': 'mean',
              'aggregation_level': 'sum',
              'L3': [
                  {'legend': 'level_l1_l2_l3_0',
                   'aggregation_freq': 'mean',
                   'aggregation_level': 'sum'}
              ]}
         ]},
        {'legend': 'level_l1_1',
         'aggregation_freq': 'mean',
         'aggregation_level': 'sum'}
    ]}
    freq_table = 'M'
    plot = Table(
        data=data,
        table_config=table_config,
        title='test_table',
        token=token,
        source='me',
        notes='a note',
        freq_table=freq_table,
        prefix_unit='bananas',
    )
    plot.publish()
    resampled = data.resample(freq_table).mean()
    assert (plot._resample_data(data)[data.columns] == resampled).values.all()
