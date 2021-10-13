from dw_squared.plot import DWSquared, _DWSquared
from dw_squared.area import Area
from dw_squared.bar import StackedBar
from dw_squared.line import Lines
from dw_squared.seasonal import Seasonal


PLOT_TYPE = {
	'area': Area,
    'stacked': StackedBar,
    'line': Lines,
    'seasonal': Seasonal,
    'undefined': _DWSquared
}

