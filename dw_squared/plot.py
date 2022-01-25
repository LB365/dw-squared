from itertools import cycle
import json
import requests as r
from pandas import Timestamp
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta

import pandas as pd
import datawrapper

from dw_squared import nest_update

class _DWSquared():
    def __init__(self, title, token) -> None:
        self.title = title
        self.dw = datawrapper.Datawrapper(access_token=token)

    def _update_data(self, data, transformation, *args, **kwargs) -> pd.DataFrame:
        search = {x['title']: x['id'] for x in self.dw.get_charts()}
        id = search[self.title]
        data = transformation(data, *args, **kwargs)
        self.dw.add_data(id, data=data)
        return self.dw.publish_chart(id)


class DWSquared(_DWSquared):
    def __init__(self,
                 title: str,
                 token: str,
                 height: int = 600,
                 width: int = 600,
                 graph_start: Timestamp=None,
                 graph_end: Timestamp=None,
                 source: str = '',
                 notes: str = '',
                 reset=False):
        super().__init__(title, token)
        self.height, self.width = height, width
        self.source, self.notes = source, notes
        self.graph_start, self.graph_end = graph_start, graph_end
        self._metadata = {} if not reset else {'visualize': {}}
        self._chart = None

    @property
    def metadata(self):
        if not self._metadata:
            charts = self.get_charts(self.title)
            if charts:
                props = self.dw.chart_properties(charts[0]['id'])
                self._metadata = props['metadata']
        return self._metadata


    @property
    def default_publish(self):
        return {
            'publish': {
                'blocks': {
                    'download-image': True,
                    'logo': False,
                },
                'chart-height': self.height,
                'chart-width': self.width
            }
        }

    @property
    def today(self):
        now = dt.utcnow()
        return dt(now.year, now.month, now.day)

    def slice_and_reset_index(self, data:pd.DataFrame):
        _range = [self.graph_start, self.graph_end]
        date_range = [f"{x:%Y-%m-%d}" if x is not None else None for x in _range]
        return data.loc[slice(*date_range)].reset_index()

    @property
    def today_line(self):
        today_str = self.today.strftime('%d/%m/%Y %H:%M')
        range_annotation = {
            'range-annotations': [
                {
                    'x0': today_str,
                    'x1': today_str,
                    'type': 'x',
                    'color': '#00344c',
                    'display': 'line',
                    'opacity': 28,
                    'strokeType': 'solid',
                    'strokeWidth': 1
                }
            ],
        }
        return range_annotation

    def get_charts(self, search='', *args, **kwargs):
        return self.dw.get_charts(search=search, *args, **kwargs)

    @property
    def chart(self):
        raise NotImplementedError()

    @property
    def compute_metadata(self):
        raise NotImplementedError()

    def decription(self):
        return self.dw.update_description(
            self.chart['id'],
            source_name=self.source,
        )

    @property
    def initial_properties(self):
        return {
            'annotate': {
                'notes': self.notes,
            }
        }

    def publish(self):
        self.decription()
        extra_properties = self.compute_metadata()
        self._metadata = nest_update(self.metadata, extra_properties)
        self.dw.update_metadata(self.chart['id'], self.metadata)
        search = {x['title']: x['id'] for x in self.dw.get_charts()}
        if self.title in search:
            self.dw.delete_chart(search[self.title])
        return self.dw.publish_chart(self.chart['id'])
