from typing import Union, List, Any
import requests as r
from datetime import datetime as dt

import pandas as pd
import datawrapper

from dw_squared.transform import (
    generate_seasonal_frame,
    compute_seasonal_stats)


class DWSquared():
    def __init__(self, token=None):
        self.dw = datawrapper.Datawrapper(access_token=token)
    
    @property
    def today():
        now = dt.utcnow()
        return dt(now.year,now.month, now.day) 

    def get_charts(self, search='', *args, **kwargs):
        return self.dw.get_charts(search=search, *args, **kwargs)


class SWSquaredSeasonal(DWSquared):
    def __init__(self, token=None):
        super().__init__(token)
    
    def dw_create_plot(self, title, seasonal_data:pd.DataFrame):
        self.dw.create_chart(title, chart_type='d3-lines', data=seasonal_data)
                