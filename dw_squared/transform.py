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

    resampled = (series.resample(freq).agg(agg))

    if interpolation is not None:
        resampled = resampled.interpolate(method=interpolation)

    df = (resampled
          .reset_index()
          .assign(year=lambda x: x['index'].dt.year,
                  index=lambda x: x['index'].dt.strftime(f'%d-%m-{now.year}'))
          .set_index(['index', 'year'])
          .unstack(1)
          )
    df.index = pd.to_datetime(df.index, format="%d-%m-%Y", errors='coerce')
    df = df.sort_index().resample(freq).agg(agg)
    return df[series.columns[0]]


def compute_seasonal_stats_unfolded(series, interpolation, freq,
                                    agg, cutoff_year: int = dt.utcnow().year):

    resampled = (series.resample(freq).agg(agg))
    if interpolation is not None:
        resampled = resampled.interpolate(method=interpolation)

    selected_formated = [resampled.index[0], dt(cutoff_year, 1, 1)]
    stats = {
        'min': {
            'name': name_stats('Min', selected_formated),
            'func': 'min',
        },
        'max': {
            'name': name_stats('Max', selected_formated),
            'func': 'max',
        },
        'mean': {
            'name': name_stats('Mean', selected_formated),
            'func': 'mean',
        }
    }
    _stats = {k: v['name'] for k, v in stats.items()}

    seasonal = resampled.loc[:dt(cutoff_year, 1, 1)]
    unfold_grouping = {
        'D': seasonal.index.dayofyear,
        'B': seasonal.index.dayofyear,
        'W': seasonal.index.weekofyear,
        'M': seasonal.index.monthofyear
    }
    f_unfold = {
        'D': lambda x: x.index.dayofyear,
        'B': lambda x: x.index.dayofyear,
        'W': lambda x: x.index.weekofyear,
        'M': lambda x: x.index.monthofyear

    }
    seasonal = (seasonal
                .groupby(unfold_grouping[freq])
                .agg(("min", "max", "mean"))
                .rename(columns=_stats)
                [series.columns[0]])
    result = (resampled
              .assign(key=f_unfold[freq])
              .merge(seasonal.reset_index(), left_on='key', right_index=True)
              .drop(["key", "index"], axis=1))
    print(result)
    return result, stats


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
