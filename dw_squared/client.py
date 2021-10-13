from datetime import datetime as dt

import pandas as pd
import datawrapper

from dw_squared.transform import (
    generate_seasonal_frame,
    compute_seasonal_stats)


class DWSquared():
    def __init__(self, height: int = 600, width: int = 600, token=None):
        self.dw = datawrapper.Datawrapper(access_token=token)
        self.height, self.width = height, width
        self._chart = None

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
    def today_line(self):
        today_str = self.today.strftime('%d/%m/%Y %H:%M')
        return {
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

    @property
    def today(self):
        now = dt.utcnow()
        return dt(now.year, now.month, now.day)

    def get_charts(self, search='', *args, **kwargs):
        return self.dw.get_charts(search=search, *args, **kwargs)


class Seasonal(DWSquared):

    def __init__(self,
                 series: pd.Series,
                 title: str = '',
                 source: str = '',
                 prefix_unit: str = '',
                 notes: str = '',
                 freq_graph: str = 'D',
                 aggregation_freq_graph: str = 'mean',
                 cutoff_year: int = None,
                 height: int = None,
                 width: int = None,
                 token: str = None,
                 ):
        super().__init__(height, width, token)
        self.series = series
        self.title = title
        self.source = source
        self.notes = notes
        self.prefix_unit = prefix_unit
        self.freq_graph = freq_graph
        self.aggregation_freq_graph = aggregation_freq_graph
        self.cutoff_year = cutoff_year
        if self.cutoff_year is None:
            self.cutoff_year = self.today.year
        _data = generate_seasonal_frame(
            self.series, self.freq_graph, self.aggregation_freq_graph)
        self._data_stats, self.columns_definition = compute_seasonal_stats(
            _data, cutoff_year=self.cutoff_year)
        self._data_stats = self._data_stats.reset_index()

    @property
    def chart(self):
        if self._chart is None:
            self._chart = self.dw.create_chart(
                self.title, chart_type='d3-lines', data=self._data_stats)
        return self._chart

    def description(self):
        self.dw.update_description(
            self.chart['id'],
            source_name=self.source
        )

    def metadata(self):
        name = self._data_stats.columns[1]
        self.columns_definition['min']['name']
        properties = {
            'data': {
                'annotate': {
                    'notes': self.notes,
                },
                'describe': {
                    'source-name': self.source,
                },
                'column-format': {
                    str(name): {
                        'type': 'auto',
                        'number-append': f' {self.prefix_unit}',
                    }
                }
            },
            'visualize': {
                'x-grid': 'off',
                'y-grid': 'on',
                'scale-y': 'linear',
                'sharing': {
                    'auto': True,
                    'enabled': False
                },
                'labeling': 'right',
                'base-color': 7,
                'label-colors': True,
                'label-margin': 120,
                'line-dashes': {
                    self.columns_definition['mean']['name']: 3
                },
                'line-widths': {
                    self.columns_definition['min']['name']: 3,
                    self.columns_definition['max']['name']: 3,
                    self.columns_definition['mean']['name']: 3
                },
                'custom-colors': {
                    self.columns_definition['mean']['name']: '#15607a',
                    self.columns_definition['max']['name']: '#ffffff',
                    self.columns_definition['min']['name']: '#ffffff',
                },
                'interpolation': 'linear',
                'show-tooltips': True,
                'x-tick-format': 'MMMM',
                'y-grid-format': 'auto',
                'y-grid-labels': 'outside',
                'chart-type-set': True,
                'custom-range-x': [
                    '',
                    ''
                ],
                'custom-range-y': [
                    '',
                    ''
                ],
                'custom-ticks-x': '',
                'custom-ticks-y': '',
                'connector-lines': True,
                'tooltip-number-format': '0,0.[00]',
                'tooltip-use-custom-formats': True,
                'tooltip-x-format': 'll',
                'y-grid-subdivide': True,
                'line-value-labels': True,
                'custom-area-fills': [
                    {
                        'to': self.columns_definition['max']['name'],
                        'from': self.columns_definition['min']['name'],
                        'color': '#cccccc',
                        'opacity': 0.3,
                        'interpolation': 'linear'
                    }
                ],
            }
        }
        properties.update(self.default_publish)
        properties['visualize'].update(self.today_line)
        self.dw.update_metadata(self.chart['id'], properties)

    def publish(self):
        self.description()
        self.metadata()
        search = self.dw.get_charts(search=self.title)
        for s in search:
            self.dw.delete_chart(s['id'])
        self.dw.publish_chart(self.chart['id'])
        print(self.chart['id'])
