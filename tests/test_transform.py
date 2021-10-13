from dw_squared.transform import name_stats, generate_seasonal_frame, compute_seasonal_stats
from datetime import datetime as dt
import pandas as pd


def test_name_stats():
    name = 'hello'
    range_date = pd.date_range(start=dt(2001,1,1), end=dt(2002,3,1), freq='M')
    assert name_stats(name, range_date) == 'hello 01-02'

def test_generate_seasonal_frame():
    range_date = pd.date_range(start=dt(2001,1,1), end=dt(2008,1,1), freq='D') 
    this_year = dt.utcnow().year
    this_year = pd.date_range(start=dt(this_year, 1, 1), end=dt(this_year, 12, 31), freq='D')
    data = pd.Series([1 for _ in range_date], index=range_date, name='serie')
    df = generate_seasonal_frame(data, freq='D', agg='mean')
    assert df.shape == (365, 8)
    assert list(df.columns) == [x for x in range(2001, 2009)]
    assert list(df.index) == list(this_year)

def test_compute_seasonal_stats():
    range_date = pd.date_range(start=dt(2001,1,1), end=dt(2008,1,1), freq='D') 
    this_year = dt.utcnow().year
    this_year = pd.date_range(start=dt(this_year, 1, 1), end=dt(this_year, 12, 31), freq='D')
    data = pd.Series([date.year for date in range_date], index=range_date, name='serie')
    df = generate_seasonal_frame(data, freq='D', agg='mean')
    stats, meta = compute_seasonal_stats(df, 2008)
    assert stats.iloc[0, 0] == 2008
    assert stats.iloc[0, 1] == 2001
    assert stats.iloc[0, 2] == 2007
    assert stats.iloc[0, 3] == sum(range(2001, 2008)) / len(list(range(2001, 2008))) 
    assert list(stats.columns[-3:]) == [x['name'] for x in meta.values()]