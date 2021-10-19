from typing import Dict
import pandas as pd
from pandas import Timestamp

from dw_squared.client import DWSquared

PRETTY_DATES = {
    'D': '%d %b',
    'W': '%d %b',
    'M': "%b '%y",
    'Q': "Q%q '%y",
    'A': '%Y',
}

SPARKLINE_DATES = {
    'D': '-%dM%m',
    'W': '%yW%V',
    'M': "%yM%-m",
    'Q': "%yQ%q",
    'A': '%y',
}

BACKGROUND = {
    'L1': "#ffffff",
    'L2': "#ffffff", #"#82f5cf",
    'L3': "#ffffff",
}
FONT_SIZE = {
    'L1': 1,
    'L2': 1,
    'L3': 0.8,
}
TOP_BORDER = {
    'L1': '1px',
    'L2': 'none',
    'L3': 'none',
}
BOTTOM_BORDER = {
    'L1': '1px',
    'L2': 'none',
    'L3': 'none',
}
BOLD = {
    'L1': True,
    'L2': False,
    'L3': False,
}


def within_key(dictionary, key):
    result = {
        level: list()
        for level in ['L1', 'L2', 'L3']
    }
    if 'L1' in dictionary:
        for l1 in dictionary['L1']:
            result['L1'].append(l1[key])
            if 'L2' in l1:
                for l2 in l1['L2']:
                    result['L2'].append(l2[key])
                    if 'L3' in l2:
                        for l3 in l2['L3']:
                            result['L3'].append(l3[key])
    return result


def triple_loop_list(dictionary, key):
    result = list()
    if 'L1' in dictionary:
        for l1 in dictionary['L1']:
            result.append(l1[key])
            if 'L2' in l1:
                for l2 in l1['L2']:
                    result.append(l2[key])
                    if 'L3' in l2:
                        for l3 in l2['L3']:
                            result.append(l3[key])
    return result


def triple_loop_dict(dictionary, key, val):
    result = dict()
    if 'L1' in dictionary:
        for l1 in dictionary['L1']:
            if 'L2' in l1:
                for l2 in l1['L2']:
                    if 'L3' in l2:
                        for l3 in l2['L3']:
                            result[l3[key]] = l3[val]
                    result[l2[key]] = l2[val]
            result[l1[key]] = l1[val]
    return result


class Table(DWSquared):
    def __init__(self,
                 table_config: Dict,
                 freq_table: str,
                 data: pd.DataFrame = None,
                 title: str = '',
                 source: str = '',
                 prefix_unit: str = '',
                 graph_start: Timestamp=None,
                 graph_end: Timestamp=None,
                 notes: str = '',
                 height: int = None,
                 width: int = None,
                 token: str = None,
                 *args,
                 **kwargs,
                 ):
        super().__init__(title, token, height, width, 
        graph_start, graph_end, source, notes)
        self.frame = data
        self.title = title
        self.source = source
        self.notes = notes
        self.prefix_unit = prefix_unit
        self.freq_table = freq_table
        self.table_config = table_config
        self._data = self.reshape_data(self.frame)

    @property
    def chart(self):
        if self._chart is None:
            self._chart = self.dw.create_chart(
                self.title, chart_type='tables', data=self._data)
        return self._chart

    def to_pretty_table(self, frame: pd.DataFrame):
        _frame = frame.copy()
        _frame.index = (_frame
                        .index
                        .to_period(self.freq_table)
                        .strftime(PRETTY_DATES[self.freq_table])
                        )
        _frame = _frame.T
        _frame.index.name = self.prefix_unit
        return _frame

    def to_sparkline(self, frame: pd.DataFrame):
        _frame = frame.copy()
        _frame.index = (_frame
                        .index
                        .to_period(self.freq_table)
                        .strftime(SPARKLINE_DATES[self.freq_table])
                        )
        _frame = _frame.T
        _frame.index.name = self.prefix_unit
        return _frame

    def order_and_indent(self, frame):

        prefixes = {
            'L1': '',
            'L2': '&nbsp&nbsp',
            'L3': '&nbsp&nbsp&nbsp&nbsp',
        }

        levels = within_key(self.table_config, 'legend')
        cols = triple_loop_list(self.table_config, "legend")
        self.level_cols = [key for c in cols for key,
                           val in levels.items() if c in val]
        new_cols = {col: prefixes[lev]+col for lev,
                    col in zip(self.level_cols, cols)}
        return frame[cols].rename(columns=new_cols)

    def _resample_data(self, frame: pd.DataFrame):
        config_agg = triple_loop_dict(
            self.table_config, 'legend', 'aggregation_freq')
        return frame.resample(self.freq_table).agg(config_agg)

    def reshape_data(self, frame: pd.DataFrame):
        self._resampled_frame = self._resample_data(frame)
        indented_frame = self.order_and_indent(self._resampled_frame)
        pretty = self.to_pretty_table(indented_frame)
        sparky = self.to_sparkline(indented_frame)
        _, self.n_sparky = sparky.shape
        df = pd.concat((sparky, pretty), axis=1)
        df.index = df.index.rename(self.prefix_unit)
        return df.reset_index()

    def today_position(self):
        return (self._resampled_frame.shape[0] +
                sum(self._resampled_frame.index < self.today))

    def update_data(self, frame):
        self._update_data(frame, self.reshape_data)

    @property
    def update_row_level_style(self):
        row_properties = dict()
        for i, row in enumerate(self.level_cols):
            name = f'row-{i}'
            row_properties[name] = {
                "borderBottom": BOTTOM_BORDER[row],
                "borderBottomColor": "#333333",
                "borderTop": TOP_BORDER[row],
                "borderTopColor": "#333333",
                'style': {},
            }
            row_properties[name]['style'].update(
                {'background': BACKGROUND[row],
                 'fontSize': FONT_SIZE[row],
                 'bold': BOLD[row],
                 'italic': False,
                 'underline': False}
            )
        row_properties[name]['borderBottom'] = "3px"
        row_properties[name]['borderBottomColor'] = "#333333"
        return row_properties

    @property
    def update_cols_style(self):
        now = self.today_position()
        col_properties = dict()
        for i, row in enumerate(self._data.columns):
            col_properties[row] = {
                'sortable': False,
                'showOnDesktop': True,
                'showOnMobile': True,
                'sparkline': {},
                'format': '0.0',
                'fixedWidth': False,
                'minWidth': 15,
            }
            if i in (now + 1, now + 2):
                col_properties[row].update({'borderLeft': "1px",
                                            'borderLeftColor': "#333333"})
            if i > 0 and i <= self.n_sparky:
                col_properties[row].update({'fixedWidth': True,
                                            'minWidth': 150})
                col_properties[row]['sparkline'] = {
                    'color': "#18a1cd",
                    'dotFirst': True,
                    'height': 20,
                    'stroke': 2,
                    'dotLast': True,
                    'enabled': True,
                    'type': "line",
                }
        return col_properties

    def metadata(self):
        extra_properties = {
            'visualize': {
                "striped": True,
                "header": {
                    "style": {
                        "bold": True,
                        "fontSize": 0.8,
                    },
                    "borderTop": "3px",
                    "borderBottom": "1px",
                    "borderTopColor": "#333333",
                    "borderBottomColor": "#333333",
                },
                "compactMode": True,
                "rows": {},
                'columns': {}
            }
        }
        extra_properties["visualize"]["rows"] = self.update_row_level_style
        extra_properties["visualize"]["columns"] = self.update_cols_style
        extra_properties.update(self.default_publish)
        extra_properties.update(self.initial_properties)
        self.dw.update_metadata(self.chart['id'], extra_properties)
