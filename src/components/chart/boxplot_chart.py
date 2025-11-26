import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.components.chart.chart import Chart
from src.components.chart.chart_controls import ChartControls
from src.components.enums import DataType, UncertaintyInterval
from src.util.constants import get_model_by_name, get_model_color_by_name

SCENARIO_AXIS_LABEL_FONT_SIZE = 10


class BoxplotChart(Chart):
  """Chart class for displaying boxplot visualizations"""

  def __init__(self, controls: ChartControls):
    super().__init__(controls)
    self._reload_data()
    self._start_date_str, self._end_date_str = self._calculate_data_time_range()
    self._fig = go.Figure()

    self.refresh_fig()

  def _calculate_data_time_range(self) -> tuple[str, str]:
    min_date: pd.Timestamp = pd.Timestamp.max
    max_date: pd.Timestamp = pd.Timestamp.min
    for scenario in self.controls.scenarios:
      scenario_df = self._raw_df.query('scenario_id == @scenario.id')
      scenario_min_date = scenario_df['target_end_date'].min()
      scenario_max_date = scenario_df['target_end_date'].max()
      if scenario_min_date < min_date:
        min_date = scenario_min_date
      if scenario_max_date > max_date:
        max_date = scenario_max_date
      if min_date == pd.Timestamp.max:
        raise ValueError(f'No start date found for scenario {scenario.name}')
      if max_date == pd.Timestamp.min:
        raise ValueError(f'No end date found for scenario {scenario.name}')
    return min_date.strftime('%Y-%m-%d'), max_date.strftime('%Y-%m-%d')

  def _wrap_vertical_text(self, text: str, row_height: float, font_size: int) -> str:
    """
    Wrap text for vertical display based on available subplot height.

    Args:
      text: The text to wrap
      row_height: Height of the row in paper coordinates (0-1)
      font_size: Font size in pixels

    Returns:
      Text with <br> tags for line breaks
    """
    if not text:
      # TODO: add debug logging
      return ''

    # Estimate characters per line based on row height
    # Figure height calculation matches refresh_fig method
    num_rows = len(self.controls.scenarios)
    figure_height_px = 400 + (200 * max(0, num_rows - 1))
    row_height_px = row_height * figure_height_px

    # Estimate characters that fit: account for font size and some padding
    # For vertical text, each character is roughly font_size pixels tall
    # Use 80% of available height to leave some padding
    max_chars_per_line = int((row_height_px * 0.8) / font_size)

    # Ensure minimum of 10 characters per line for readability
    max_chars_per_line = max(10, max_chars_per_line)

    # If text fits in one line, return as-is
    if len(text) <= max_chars_per_line:
      return text

    # Split text into words and build lines
    words = text.split()
    lines: list[str] = []
    current_line = ''

    for word in words:
      # If adding this word would exceed the limit, start a new line
      test_line = f'{current_line} {word}'.strip() if current_line else word
      if len(test_line) <= max_chars_per_line:
        current_line = test_line
      else:
        if current_line:
          lines.append(current_line)
        current_line = word

    if current_line:
      lines.append(current_line)

    return '<br>'.join(lines)

  def __eq__(self, other):
    return isinstance(other, BoxplotChart) and self.controls == other.controls

  def __hash__(self):
    return hash(self.get_key())

  def refresh_fig(self) -> go.Figure:
    # handle empty properties
    if not (
      self.controls.scenarios
      and self.controls.models
      and self.controls.location
      and self.controls.target
    ):
      self._create_empty_figure()
      return self._fig

    # create boxplot for each scenario
    num_rows = len(self.controls.scenarios)
    num_cols = 1
    self._fig = make_subplots(
      rows=num_rows,
      cols=num_cols,
      vertical_spacing=0.1,
    )

    # start with the raw dataframe
    df = self._raw_df

    # filter for given age group
    df = df.query('age_group == @self.controls.age_group.input_value')

    # filter for ensemble model, specifically
    ensemble_model_id = get_model_by_name('Ensemble')['id']  # noqa: F841
    df = df.query('model_name == @ensemble_model_id')

    for i, scenario in enumerate(self.controls.scenarios, start=1):
      scenario_df = df.query('scenario_id == @scenario.id')
      trace = go.Box(
        marker_color=get_model_color_by_name('Ensemble'),
        name='',
        showlegend=False,
      )
      if self.controls.x_axis:
        trace.x = scenario_df[self.controls.x_axis]
      else:
        trace.y = scenario_df[self.controls.y_axis]
      self._fig.add_trace(
        trace,
        row=i,
        col=1,
      )

      # Add scenario name as vertical text annotation to the right of the boxplot
      subplot_idx = ((i - 1) * num_cols) + 1
      x_axis = self._fig.layout[f'xaxis{subplot_idx}']
      # Position to the right of subplot domain using paper coordinates
      # x_axis.domain is a list [min, max] in paper coordinates
      x_domain = getattr(x_axis, 'domain', [0.55, 1.0])
      if isinstance(x_domain, (list, tuple)) and len(x_domain) >= 2:
        x_paper = x_domain[1] + 0.02
      else:
        x_paper = 1.02
      # Calculate y position to center vertically in the row
      vertical_spacing = 0.1
      row_height = (1.0 - (vertical_spacing * (num_rows - 1))) / num_rows
      y_top = 1.0 - ((i - 1) * (row_height + vertical_spacing))
      y_bottom = y_top - row_height
      y_paper = (y_top + y_bottom) / 2

      # Wrap text if it's too long for the subplot height
      wrapped_text = self._wrap_vertical_text(
        scenario.description, row_height, SCENARIO_AXIS_LABEL_FONT_SIZE
      )

      self._fig.add_annotation(
        text=wrapped_text,
        xref='paper',
        yref='paper',
        x=x_paper,
        y=y_paper,
        xanchor='left',
        yanchor='middle',
        textangle=-90,
        showarrow=False,
        font=dict(size=SCENARIO_AXIS_LABEL_FONT_SIZE),
      )

    # plot annotations
    self._plot_annotations()

    # update axes
    self._fig.update_xaxes(showspikes=False)
    self._fig.update_yaxes(showspikes=False)

    # calculate global min/max across all subplots for synchronized axes
    x_range, y_range = self._calculate_axes_ranges(df, num_rows)

    if x_range is not None or y_range is not None:
      for i in range(1, num_rows + 1):
        if x_range is not None:
          self._fig.update_xaxes(range=x_range, row=i, col=1)
        if y_range is not None:
          self._fig.update_yaxes(range=y_range, row=i, col=1)

    # Add x-axis label only to the last row (bottom plot)
    if num_rows > 1:
      last_row_xaxis_name = f'xaxis{num_rows}'
    else:
      last_row_xaxis_name = 'xaxis'
    self._fig.layout[last_row_xaxis_name].title = dict(
      text=self.controls.target.display_value,
    )

    self._fig.update_layout(
      hovermode='closest',
      height=400 + (200 * max(0, num_rows - 1)),
      title=self.get_title(),
      title_subtitle_text=self.get_subtitle(),
      uirevision=self.__hash__(),
      showlegend=False,
    )

    self.set_theme()

    return self._fig

  def get_title(self) -> str:
    return f'{self.controls.target.display_value} Distribution'

  def get_subtitle(self) -> str:
    return (
      f'Pathogen: {self.controls.pathogen}'
      + f' | Location: {self.controls.location.name}'
      + f' | Age group: {self.controls.age_group.display_value}'
      + f' | During: {self._start_date_str} - {self._end_date_str}'
    )

  def _reload_data(self):
    """
    Reload data, for example if a variable changed, e.g. round number, location, target, etc.
    This is called by individual update methods when data-dependent fields change.
    """
    new_raw_df = Chart.collect_data(
      DataType.QUANTILE,
      self.controls.round_num,
      self.controls.location.name,
      self.controls.target.input_value,
    )
    self._raw_df = new_raw_df

  def _calculate_axes_ranges(
    self, df: pd.DataFrame, num_rows: int
  ) -> tuple[list[float] | None, list[float] | None]:
    """
    Calculate the x and y axis ranges for all subplots in the chart.
    This is a stub implementation - full implementation to be added later.
    Zoom logic:
      * If current_zoom is set in the controls, use it
      * If saved_zoom is set in the controls but not current_zoom, set current_zoom to saved_zoom and use it
      * If neither current_zoom nor saved_zoom is set, calculate the ranges from the data
    """
    has_current_zoom = (
      self.controls.current_zoom is not None and self.controls.current_zoom.is_valid()
    )

    if has_current_zoom:
      x_range = [self.controls.current_zoom.x.min, self.controls.current_zoom.x.max]
      y_range = [self.controls.current_zoom.y.min, self.controls.current_zoom.y.max]
      return x_range, y_range

    has_saved_zoom = self.controls.saved_zoom is not None and self.controls.saved_zoom.is_valid()

    if has_saved_zoom:
      # Set current_zoom to saved_zoom for first load
      self.controls.current_zoom = self.controls.saved_zoom
      x_range = [self.controls.saved_zoom.x.min, self.controls.saved_zoom.x.max]
      y_range = [self.controls.saved_zoom.y.min, self.controls.saved_zoom.y.max]
      return x_range, y_range

    # Calculate from data (stub - full implementation to be added)
    x_min = None
    x_max = None
    y_min = None
    y_max = None

    if self.controls.x_axis:
      for scenario in self.controls.scenarios:
        scenario_df = df.query('scenario_id == @scenario.id')
        scenario_x_values = scenario_df[self.controls.x_axis]
        if scenario_x_values.empty:
          continue
        scenario_x_min = scenario_x_values.min()
        scenario_x_max = scenario_x_values.max()
        if scenario_x_min is not None and scenario_x_max is not None:
          if x_min is None or scenario_x_min < x_min:
            x_min = scenario_x_min
          if x_max is None or scenario_x_max > x_max:
            x_max = scenario_x_max

    if self.controls.y_axis:
      for scenario in self.controls.scenarios:
        scenario_df = df.query('scenario_id == @scenario.id')
        scenario_y_values = scenario_df[self.controls.y_axis]
        if scenario_y_values.empty:
          continue
        scenario_y_min = scenario_y_values.min()
        scenario_y_max = scenario_y_values.max()
        if scenario_y_min is not None and scenario_y_max is not None:
          if y_min is None or scenario_y_min < y_min:
            y_min = scenario_y_min
          if y_max is None or scenario_y_max > y_max:
            y_max = scenario_y_max

    if x_min is not None and x_max is not None and y_min is not None and y_max is not None:
      x_range = [x_min, x_max]
      y_range = [y_min, y_max]
      # Set current_zoom to calculated values (but don't set saved_zoom)
      from src.components.chart.chart_properties import Zoom

      self.controls.current_zoom = Zoom(
        x_min=x_range[0], x_max=x_range[1], y_min=y_range[0], y_max=y_range[1]
      )
    elif x_min is not None and x_max is not None:
      x_range = [x_min, x_max]
      y_range = None
    elif y_min is not None and y_max is not None:
      x_range = None
      y_range = [y_min, y_max]
    else:
      x_range = None
      y_range = None

    return x_range, y_range

  def update_uncertainty_interval(self, uncertainty_interval: str | None):
    """
    Update the uncertainty interval.
    """
    self.controls.uncertainty_interval = (
      UncertaintyInterval.from_display_value(uncertainty_interval) if uncertainty_interval else None
    )
    self.refresh_fig()
