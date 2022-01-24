from typing import Dict, List, Optional, Tuple
from itertools import chain, repeat
from numpy.lib.twodim_base import tri
import yaml

import pandas as pd
import numpy as np

from tshistory.api import timeseries
from tqdm.contrib.concurrent import thread_map

from dw_squared.plot import _DWSquared, DWSquared
from dw_squared.area import Area
from dw_squared.bar import StackedBar
from dw_squared.line import Lines
from dw_squared.seasonal import Seasonal
from dw_squared.moments import evaluate_not_none
from dw_squared.table import Table, triple_loop_list


PLOT_TYPE = {
    'area': Area,
    'stacked': StackedBar,
    'line': Lines,
    'seasonal': Seasonal,
    'table': Table,
    'undefined': _DWSquared,
    'table': Table,
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
            self.config = yaml.load(stream, Loader=yaml.FullLoader)
        self.df_config = pd.json_normalize(self.config)

    def single_config(self, title):
        config = list(filter(lambda x: x['title'] == title, self.config))[0]
        if 'graph_end' in config.keys():
            config['graph_end'] = evaluate_not_none(config['graph_end'])
        if 'graph_start' in config.keys():
            config['graph_start'] = evaluate_not_none(config['graph_start'])
        del config['series']
        return config

    def order_series(self, title: str):
        conf = list(filter(lambda x: title == x['title'], self.config))[0]
        return [s['legend'] for s in conf['series']]

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


class TableConfig():

    def __init__(self, path) -> None:
        self.path = path
        with open(self.path, 'r') as stream:
            self.config = yaml.load(stream, Loader=yaml.FullLoader)
        self.df_config = pd.json_normalize(self.config)

    def single_config(self, title):
        config = list(filter(lambda x: x['title'] == title, self.config))[0]
        if 'graph_end' in config.keys():
            config['graph_end'] = evaluate_not_none(config['graph_end'])
        if 'graph_start' in config.keys():
            config['graph_start'] = evaluate_not_none(config['graph_start'])
        return config

    def order_series(self, title: str):
        conf = list(filter(lambda x: title == x['title'], self.config))[0]
        return triple_loop_list(conf, 'legend')

    def series_queries(self, titles: List[str] = list()):
        mask = self.df_config.title.isin(titles)
        t = self.df_config[mask]['title']
        start = self.df_config[mask]['graph_start'].apply(evaluate_not_none)
        end = self.df_config[mask]['graph_end'].apply(evaluate_not_none)
        frames = []
        for x in self.config:
            if x['title'] in t.values:
                series_id = triple_loop_list(x, 'series_id')
                legend = triple_loop_list(x, 'legend')
                _dataframe = pd.DataFrame(np.array([series_id, legend]).T,
                                          columns=['series_id', 'legend'])
                _dataframe['start'] = start[mask].values[0]
                _dataframe['end'] = end[mask].values[0]
                _dataframe['revision'] = np.nan
                _dataframe['title'] = x['title']
                frames.append(
                    _dataframe.reset_index().set_index(['title', 'index']))
        return pd.concat(frames, axis=0)

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
    cols = config.order_series(title)
    kwargs = {**config.single_config(title),
              'data': data[cols],
              'token': token}
    plot = PLOT_TYPE[kwargs['chart_type']](**kwargs)
    plot.publish()


def create_single_table(data: pd.DataFrame,
                        config: TableConfig,
                        title: dict,
                        token: str):
    cols = config.order_series(title)
    _config = config.single_config(title)
    kwargs = {**_config,
              'data': data[cols],
              'table_config': _config,
              'token': token}
    plot = PLOT_TYPE[kwargs['chart_type']](**kwargs)
    plot.publish()


def update_single_plot(data: pd.DataFrame,
                       config: PlotConfig,
                       title: dict,
                       token: str):
    cols = config.order_series(title)
    kwargs = {**config.single_config(title),
              'data': data[cols],
              'token': token}
    plot = PLOT_TYPE[kwargs['chart_type']](**kwargs)
    plot.update_data(data)
