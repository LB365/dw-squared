from datetime import datetime as dt

import pandas as pd
import datawrapper


class DWSquared():
    def __init__(self,
                 height: int = 600,
                 width: int = 600,
                 source: str = '',
                 notes: str = '',
                 token=None):
        self.dw = datawrapper.Datawrapper(access_token=token)
        self.height, self.width = height, width
        self.source, self.notes = source, notes
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
    def today(self):
        now = dt.utcnow()
        return dt(now.year, now.month, now.day)

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

    def get_charts(self, search='', *args, **kwargs):
        return self.dw.get_charts(search=search, *args, **kwargs)

    @property
    def chart(self):
        raise NotImplementedError()

    def decription(self):
        raise NotImplementedError()

    def metadata(self):
        raise NotImplementedError()

    def decription(self):
        return self.dw.update_description(
            self.chart['id'],
            source_name=self.source,
        )

    def _update_data(self, data, transformation, *args, **kwargs) -> pd.DataFrame:
        id = self.dw.get_charts(search=self.title)[0]['id']
        data = transformation(data, *args, **kwargs)
        self.dw.add_data(id, data=data)

    @property
    def initial_properties(self):
        return {
            'annotate': {
                'notes': self.notes,
            }
        }

    def publish(self):
        self.decription()
        self.metadata()
        search = self.dw.get_charts(search=self.title)
        for s in search:
            self.dw.delete_chart(s['id'])
        self.dw.publish_chart(self.chart['id'])
        print(f'chart_id: {self.chart["id"]}, chart_title: {self.title}')
