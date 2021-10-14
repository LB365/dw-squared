from datetime import datetime as dt
from typing import Dict, Tuple
import pandas as pd


def name_stats(name, date_range):
    return f'{name} {date_range[0]:%y}-{date_range[-1]:%y}'


def generate_seasonal_frame(
        series: pd.DataFrame,
        interpolation=None,
        freq: str = 'W',
        agg: str = 'mean'
) -> pd.DataFrame:

    now = dt.utcnow()
    df = (series
          .reset_index()
          .assign(year=lambda x: x['index'].dt.year,
                  index=lambda x: x['index'].dt.strftime(f'%d-%m-{now.year}'))
          .set_index(['index', 'year'])
          .unstack(1)
          )
    df.index = pd.to_datetime(df.index, format="%d-%m-%Y", errors='coerce')
    df = df.sort_index().resample(freq).agg(agg)
    if interpolation is not None:
        df = df.interpolate(method=interpolation)
    return df[series.columns[0]]


def compute_seasonal_stats(
        frame: pd.DataFrame,
        cutoff_year: int = dt.utcnow().year) -> Tuple[pd.DataFrame, Dict]:

    selected = frame.columns[frame.columns < cutoff_year]
    selected_formated = [dt(year, 1, 1) for year in selected]
    stats = {
        'min': {
            'name': name_stats('Min', selected_formated),
            'func': lambda x: x[selected].min(axis=1),
        },
        'max': {
            'name': name_stats('Max', selected_formated),
            'func': lambda x: x[selected].max(axis=1),
        },
        'mean': {
            'name': name_stats('Mean', selected_formated),
            'func': lambda x: x[selected].mean(axis=1),
        }
    }
    _stats = {x['name']: x['func'] for x in stats.values()}
    return frame.assign(**_stats).drop(selected, axis=1), stats
