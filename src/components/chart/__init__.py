from src.components.chart.chart_properties import PlotType

from .boxplot_chart import BoxplotChart
from .chart import Chart
from .chart_controls import ChartControls
from .line_chart import LineChart


def create_chart(controls: ChartControls) -> Chart:
  plot_type = controls.plot_type
  if plot_type == PlotType.LINE:
    return LineChart(controls)
  elif plot_type == PlotType.BOXPLOT:
    return BoxplotChart(controls)
  else:
    raise ValueError(f'Invalid plot type: {plot_type}')


__all__ = [
  'Chart',
  'BoxplotChart',
  'LineChart',
  'ChartControls',
]
