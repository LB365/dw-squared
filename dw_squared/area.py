import pandas as pd

from dw_squared.client import DWSquared


class Area(DWSquared):
    def __init__(self,
                 frame: pd.DataFrame = None,
                 title: str = '',
                 source: str = '',
                 prefix_unit: str = '',
                 notes: str = '',
                 display_today: bool = True,
                 height: int = None,
                 width: int = None,
                 token: str = None,
                 ):
        super().__init__(title, token, height, width, source, notes)
        self.frame = frame
        self.title = title
        self.source = source
        self.notes = notes
        self.display_today = display_today
        self.prefix_unit = prefix_unit
        self._data = self.reshape_data(self.frame)

    @property
    def chart(self):
        if self._chart is None:
            self._chart = self.dw.create_chart(
                self.title, chart_type='d3-area', data=self._data)
        return self._chart

    def reshape_data(self, frame: pd.DataFrame):
        self._data = frame.reset_index()
        return self._data

    def update_data(self, frame):
        self._update_data(frame, self.reshape_data)

    def metadata(self):
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
                'scale-y': 'linear',
                'sharing': {
                    'auto': True,
                    'enabled': False
                },
		'area-opacity': 1,
		'area-separator-color': 0,
		'sort-areas': 'keep',
		'stack-areas': 'true',
                'labeling': 'top',
                'base-color': 7,
                'label-colors': True,
                'interpolation': 'linear',
                'show-tooltips': True,
                'y-grid-format': 'auto',
                'y-grid-labels': 'outside',
            }
        }
        extra_properties.update(self.default_publish)
        extra_properties.update(self.initial_properties)
        if self.display_today:
            extra_properties['visualize'].update(self.today_line)
        self.dw.update_metadata(self.chart['id'], extra_properties)
