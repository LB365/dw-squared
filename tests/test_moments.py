from dw_squared.moments import evaluate_not_none
import pandas as pd
from datetime import datetime as dt

def test_date():
    expr = '(yearstart (date "2021-5-1"))'
    assert evaluate_not_none(expr) == pd.to_datetime(dt(2021, 1, 1))
    expr = '(yearend (date "2021-5-1"))'
    assert evaluate_not_none(expr) == pd.to_datetime(dt(2021, 12, 31))
    expr = '(deltadays (date "2021-5-1") 4)'
    assert evaluate_not_none(expr) == pd.to_datetime(dt(2021, 5, 5))
    