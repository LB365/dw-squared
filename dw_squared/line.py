import pandas as pd
import numpy as np
from pandas import Timestamp

from dw_squared import PALETTE
from dw_squared.client import DWSquared


class Lines(DWSquared):
    def __init__(self,
                 data: pd.DataFrame = None,
                 title: str = '',
                 source: str = '',
                 prefix_unit: str = '',
                 notes: str = '',
                 graph_start: Timestamp = None,
                 graph_end: Timestamp = None,
                 display_today: bool = True,
                 height: int = None,
                 width: int = None,
                 token: str = None,
                 secondary=False,
                 secondary_unit='',
                 interpolation="linear",
                 *args,
                 **kwargs,
                 ):
        super().__init__(title, token, height, width,
                         graph_start, graph_end, source, notes, True)
        self.frame = data
        self.title = title
        self.source = source
        self.notes = notes
        self.display_today = display_today
        self.prefix_unit = prefix_unit
        self.secondary = secondary
        self.secondary_unit = secondary_unit
        self.interpolation = interpolation
        self._data = self.reshape_data(self.frame)

    @property
    def chart(self):
        if self._chart is None:
            self._chart = self.dw.create_chart(
                self.title, chart_type='d3-lines', data=self._data)
        return self._chart

    def reshape_data(self, frame: pd.DataFrame):
        _frame = frame.interpolate(self.interpolation)
        if self.secondary:
            assert _frame.shape[1] == 2, "Not compatible with more than two series"
            means = _frame.mean()
            stds = _frame.std()
            self.unscaled = _frame.iloc[:, -1].copy()
            self.rescaled = 0.90 * means[0] + stds[0] * \
                ((_frame.iloc[:, -1] - means[-1]) / stds[-1])
            _frame.iloc[:, 1] = self.rescaled
        self._data = self.slice_and_reset_index(_frame)
        return self._data

    def update_data(self, frame):
        self._update_data(frame, self.reshape_data)

    def compute_metadata(self):
        splits = []
        if self.secondary:
            assert self._data.shape[1] > 1, "must be multivariate and plots with secondary line"
            splits = np.array_split(self._data.set_index('index').iloc[:, -1], 5)
        palette = {legend: next(PALETTE) for legend in self._data.columns[1:]}
        label_policy = 'right' if self.secondary else 'top' if self._data.shape[1] > 2 else 'none'
        extra_properties = {
            'data': {
                'column-format': {
                    self._data.columns[1]: {
                        'type': 'auto',
                        'number-append': f' {self.prefix_unit}',
                    }
                }
            },
            'visualize': {
                'x-grid': 'ticks',
                'y-grid': 'on',
                'custom-colors': palette,
                'scale-y': 'linear',
                'labeling': label_policy,
                'base-color': 7,
                'label-colors': True,
                'interpolation': 'linear',
                'show-tooltips': False if self.secondary else True,
                'y-grid-labels': 'inside',
                "line-symbols": False,
                "text-annotations": [
                    {'x': x.index[-1].strftime('%Y/%m/%d %H:%M'),
                     "connectorLine":{
                         'enabled': True,
                         "stroke": 1,
                         'targetPadding': 1,
                         'type': "straight",
                         'arrowHead': False,
                    },
                        'y': x.iloc[-1],
                        'size': 10,
                        "align": "mc",
                        'dx': 0,
                        'dy': 40,
                        'text': f"{self.unscaled[x.index[-1]]:.1f} {self.secondary_unit}"}
                    for x in splits[:-1]] if self.secondary else [],
            }
        }
        extra_properties.update(self.default_publish)
        extra_properties.update(self.initial_properties)
        if self.display_today:
            extra_properties['visualize'].update(self.today_line)
        return extra_properties
