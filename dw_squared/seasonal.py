import pandas as pd

from dw_squared.client import DWSquared

from dw_squared import PALETTE
from dw_squared.transform import (
    compute_seasonal_stats_unfolded,
    generate_seasonal_frame,
    compute_seasonal_stats
)


class Seasonal(DWSquared):

    def __init__(self,
                 data: pd.DataFrame = None,
                 title: str = '',
                 source: str = '',
                 prefix_unit: str = '',
                 notes: str = '',
                 freq_graph: str = 'D',
                 aggregation_freq_graph: str = 'mean',
                 interpolation: str = None,
                 cutoff_year: int = None,
                 folded: bool = True,
                 height: int = None,
                 width: int = None,
                 token: str = None,
                 *args,
                 **kwargs,
                 ):
        super().__init__(title, token, height, width, source, notes)
        assert data.shape[1] == 1, "Data must be univariate for seasonal plots"
        self.series = data
        self.title = title
        self.source = source
        self.notes = notes
        self.interpolation = interpolation
        self.prefix_unit = prefix_unit
        self.freq_graph = freq_graph
        self.aggregation_freq_graph = aggregation_freq_graph
        self.cutoff_year = cutoff_year
        if self.cutoff_year is None:
            self.cutoff_year = self.today.year
        self.reshaped_data_folded(data) if folded else self.reshape_data(data)

    def reshaped_data_folded(self, series):
        self._data_stats = None
        if series is not None:
            self._data_stats, self.columns_definition = compute_seasonal_stats_unfolded(
                series, self.interpolation,
                self.freq_graph, self.aggregation_freq_graph, self.cutoff_year
            )
            self._data_stats = self._data_stats.reset_index()
        return self._data_stats

    def reshape_data(self, series):
        self._data_stats = None
        if series is not None:
            _data = generate_seasonal_frame(
                series, self.interpolation,
                self.freq_graph, self.aggregation_freq_graph
            )
            self._data_stats, self.columns_definition = compute_seasonal_stats(
                _data, cutoff_year=self.cutoff_year)
            self._data_stats = self._data_stats.reset_index()
        return self._data_stats

    @property
    def chart(self):
        if self._chart is None:
            self._chart = self.dw.create_chart(
                self.title, chart_type='d3-lines', data=self._data_stats)
        return self._chart

    def update_data(self, frame):
        self._update_data(frame, self.reshape_data)

    def metadata(self):
        name = self._data_stats.columns[1]
        self.columns_definition['min']['name']
        extra_properties = {
            'data': {
                'column-format': {
                    str(name): {
                        'type': 'auto',
                        'number-append': f' {self.prefix_unit}',
                    }
                }
            },
            'visualize': {
                'x-grid': 'ticks',
                'y-grid': 'on',
                'scale-y': 'linear',
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
                'y-grid-labels': 'inside',
                'tooltip-use-custom-formats': True,
                'tooltip-x-format': 'Do MMMM',
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
        extra_properties.update(self.default_publish)
        extra_properties.update(self.initial_properties)
        extra_properties['visualize'].update(self.today_line)
        self.dw.update_metadata(self.chart['id'], extra_properties)
