from functools import lru_cache

from src.components.chart import Chart, ChartControls, PlotType


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
  def _create_chart(self, plot_type: PlotType, controls: ChartControls) -> Chart:
    """
    Create a chart instance. This method is cached by @lru_cache.
    """
    return Chart(plot_type, controls)

  def get_chart(self, controls: ChartControls, plot_type: PlotType = PlotType.LINE) -> Chart:
    """
    Get or create a chart instance with LRU caching.

    Args:
      controls: Chart configuration parameters
      plot_type: Type of plot to create

    Returns:
      Chart object (either cached or newly created)
    """
    # Get chart from LRU cache
    chart = self._create_chart(plot_type, controls)

    # Update the chart with current controls (in case they changed)
    chart.update_controls(controls)

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
