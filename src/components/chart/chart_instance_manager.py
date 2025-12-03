from functools import lru_cache

from src.components.chart.boxplot_chart import BoxplotChart
from src.components.chart.chart import Chart
from src.components.chart.chart_controls import ChartControls
from src.components.chart.chart_properties import PlotType, Zoom
from src.components.chart.line_chart import LineChart


def create_chart(controls: ChartControls) -> Chart:
  plot_type = controls.plot_type
  if plot_type == PlotType.LINE:
    return LineChart(controls)
  elif plot_type == PlotType.BOXPLOT:
    return BoxplotChart(controls)
  else:
    raise ValueError(f'Invalid plot type: {plot_type}')


class ChartInstanceManager:
  """
  Manages chart instances using Python's built-in @lru_cache decorator.
  Provides a clean interface while leveraging the optimized LRU implementation.
  """

  def __init__(self):
    """
    Initialize the chart instance manager.
    """

  @lru_cache(maxsize=100)
  def _create_chart(self, controls: ChartControls) -> Chart:
    """
    Create a chart instance. This method is cached by @lru_cache.
    """
    return create_chart(controls)

  def get_chart(self, controls: ChartControls, current_zoom: Zoom | None = None) -> Chart:
    """
    Get or create a chart instance with LRU caching.

    Args:
      controls: Chart configuration parameters
      current_zoom: Optional current zoom to apply (calculated from relayoutData in callbacks)

    Returns:
      Chart object (either cached or newly created)
    """
    # Get chart from LRU cache (cached without considering current_zoom)
    chart = self._create_chart(controls)
    # Apply saved_zoom and current_zoom to the cached chart
    chart.update_zoom(saved_zoom=controls.saved_zoom, current_zoom=current_zoom)

    return chart

  def clear_all(self) -> None:
    """
    Clear all stored chart instances.
    """
    self._create_chart.cache_clear()

  def get_stats(self) -> dict[str, int | float]:
    """
    Get statistics about the chart instance manager.
    """
    cache_info = self._create_chart.cache_info()
    return {
      'total_instances': cache_info.currsize,
      'max_instances': cache_info.maxsize,
      'memory_usage_percent': (cache_info.currsize / cache_info.maxsize) * 100,
      'hits': cache_info.hits,
      'misses': cache_info.misses,
      'hit_rate': cache_info.hits / (cache_info.hits + cache_info.misses)
      if (cache_info.hits + cache_info.misses) > 0
      else 0,
    }
