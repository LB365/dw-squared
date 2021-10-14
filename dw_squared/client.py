from typing import Dict, List, Optional, Tuple
from pandas._config import config
import yaml
import math

import pandas as pd
import numpy as np

from tshistory.api import timeseries
from tqdm.contrib.concurrent import thread_map

from dw_squared.plot import DWSquared, _DWSquared
from dw_squared.area import Area
from dw_squared.bar import StackedBar
from dw_squared.line import Lines
from dw_squared.seasonal import Seasonal
from dw_squared.moments import evaluate_not_none


PLOT_TYPE = {
    'area': Area,
    'stacked': StackedBar,
    'line': Lines,
    'seasonal': Seasonal,
    'undefined': _DWSquared
}

TSAResult = Dict[Tuple[str, Optional[pd.Timestamp]], Optional[pd.Series]]


def safe_dt_none(x, return_type=None):
    if isinstance(x, pd.Timestamp):
        return x
    else:
        return return_type


class PlotConfig():

    def __init__(self, path) -> None:
        self.path = path
        with open(self.path, 'r') as stream:
            self.config = yaml.load(stream)
        self.df_config = pd.json_normalize(self.config)

    def single_config(self, title):
        config = list(filter(lambda x: x['title'] == title, self.config))[0]
        del config['series']
        return config

    def series_queries(self, titles: List[str] = list()):
        mask = self.df_config.title.isin(titles)
        t, s = self.df_config[mask]['title'], self.df_config[mask]['series']
        dfs = {title: pd.DataFrame.from_records(x)
               for title, x in zip(t, s)}
        df = pd.concat(dfs, ignore_index=False)
        dates = df[['start', 'end', 'revision']].applymap(evaluate_not_none)
        return pd.concat((df[['series_id', 'legend']], dates), axis=1).replace({np.nan: None})

    def series_bounds(self, titles: List[str] = list()):
        return (self.series_queries(titles)
                .groupby(['series_id', 'revision'], dropna=False)
                .agg({'start': 'min', 'end': 'max'}).replace({np.nan: None})
                .to_dict('index')
                )


def get_data(tsa: timeseries, queries: Dict = None):
    def body(item):
        key, val = item
        kwargs = dict(name=key[0],
                      from_value_date=safe_dt_none(val['start']),
                      to_value_date=safe_dt_none(val['end']),
                      revision_date=safe_dt_none(key[-1]))
        return key, tsa.get(**kwargs)

    return dict(thread_map(body, queries.items()))


def saturn_to_frame(data: TSAResult,
                    config: PlotConfig,
                    title: str):
    series = (config
              .series_queries([title])
              .xs(title, level=0)
              .set_index(['series_id', 'revision']))

    def key(name, rev):
        return series.xs([name, rev])['legend']

    def slice_range(name, rev, serie):
        bounds = series.xs([name, rev])
        start, end = bounds['start'], bounds['end']
        return serie[start: end]

    filtered = {key(n, r): slice_range(n, r, v) for (n, r), v in data.items()}
    return pd.concat(filtered, axis=1)


def create_single_plot(data: pd.DataFrame,
                       config: PlotConfig,
                       title: dict,
                       token: str):
    kwargs = {**config.single_config(title),
              'data': data,
              'token': token}
    plot = PLOT_TYPE[kwargs['chart_type']](**kwargs)
    plot.publish()


def update_single_plot(data: pd.DataFrame,
                       config: PlotConfig,
                       title: dict,
                       token: str):
    kwargs = {**config.single_config(title),
              'data': data,
              'token': token}
    plot = PLOT_TYPE[kwargs['chart_type']](**kwargs)
    plot.update_data(data)
