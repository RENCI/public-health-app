from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.components.chart.chart import Chart
from src.components.chart.chart_controls import ChartControls
from src.components.chart.chart_properties import DatetimeAxisRange, FloatAxisRange, Model, Zoom
from src.components.enums import DataType, UncertaintyInterval
from src.util.constants import get_model_color_with_uncertainty_interval


class LineChart(Chart):
  """Chart class for displaying a chart"""

  def __init__(self, controls: ChartControls):
    super().__init__(controls)
    self._raw_df = self._raw_df.set_index(self.controls.x_axis)

    self.refresh_fig()

  def __eq__(self, other):
    return isinstance(other, LineChart) and self.controls == other.controls

  def __hash__(self):
    return hash(self.get_key())

  def refresh_fig(self, current_zoom: Zoom | None = None) -> go.Figure:
    # handle empty properties
    if not (
      self.controls.scenarios
      and self.controls.models
      and self.controls.location
      and self.controls.target
    ):
      self._create_empty_figure()
      return self._fig

    num_rows = len(self.controls.scenarios)

    # define fixed dimensions
    SUBPLOT_HEIGHT = 300  # fixed height per subplot in pixels
    FIXED_SPACING = 60  # fixed spacing between subplots in pixels

    # calculate total figure height accounting for fixed spacing
    chart_total_height = (SUBPLOT_HEIGHT * num_rows) + (FIXED_SPACING * (num_rows - 1))

    # calculate vertical_spacing as a fraction of total height
    # this ensures the actual pixel spacing remains constant
    if num_rows > 1:
      vertical_spacing = FIXED_SPACING / chart_total_height
    else:
      vertical_spacing = 0  # no spacing needed for single subplot

    # start with the raw dataframe
    df = self._raw_df

    # filter for given age group
    df = df.query('age_group == @self.controls.age_group.input_value')

    # create subplots
    self._fig = make_subplots(
      rows=num_rows,
      cols=1,
      vertical_spacing=vertical_spacing,
      row_heights=[1] * num_rows,
      subplot_titles=[f'{s.name.split("-")[0]}. {s.description}' for s in self.controls.scenarios],
    )

    # add traces for each scenario
    for i, scenario in enumerate(self.controls.scenarios, start=1):
      scenario_df = df.query('scenario_id == @scenario.id')

      # add traces for each model
      for model in self.controls.models:
        self._plot_uncertainty_interval(scenario_df, model, row_num=i)
        self._plot_primary_line(scenario_df, model, row_num=i)

      self._plot_gold_standard_line(self._gold_std_df, row_num=i)

    # plot annotations
    self._plot_annotations()

    # apply spike guides for each axis in the chart viewport
    self._fig.update_xaxes(showspikes=True, spikemode='across', spikesnap='cursor')
    self._fig.update_yaxes(showspikes=True, spikemode='across')

    # calculate chart min/max across all subplots for synchronized axes
    self._set_axes_ranges(df, self._gold_std_df, num_rows, current_zoom)

    self._fig.update_yaxes(title_text=self.controls.target.display_value)

    # add title, subtitle, and height to the figure layout
    self._fig.update_layout(
      hovermode='x unified',
      height=chart_total_height + 180,
      title=self.get_title(),
      title_subtitle_text=self.get_subtitle(),
      uirevision=self.__hash__(),
    )

    self.set_theme()

    return self._fig

  def _take_valid_min(
    self, first: float | datetime | None, second: float | datetime | None
  ) -> float | datetime | None:
    """Take the valid minimum of two values. Attempts to find a non-None value, but could return None if both are None."""
    return (
      min(first, second)
      if first is not None and second is not None
      else first
      if first is not None
      else second
    )

  def _take_valid_max(
    self, first: float | datetime | None, second: float | datetime | None
  ) -> float | datetime | None:
    """Take the valid maximum of two values. Attempts to find a non-None value, but could return None if both are None."""
    return (
      max(first, second)
      if first is not None and second is not None
      else first
      if first is not None
      else second
    )

  def _calculate_axes_ranges(
    self, df: pd.DataFrame, gold_std_df: pd.DataFrame, current_zoom: Zoom | None = None
  ) -> Zoom | None:
    """
    Calculate the x and y axis ranges for all subplots in the chart.
    Zoom logic:
      * If the current zoom is not None and is different from saved_zoom, use the current zoom
      * If the Use Chart Zoom button is pressed, set both zooms to the current zoom values
      * If the zoom is manually changed through either the chart or the controls, do not change saved_zoom, only current_zoom
      * If the insight is saved, set saved_zoom to current_zoom
      * If saved_zoom exists, use it (respects user's saved zoom or previously calculated zoom)
      * If saved_zoom is None, calculate from data combining both projections and gold standard
    """
    if current_zoom is not None:
      return current_zoom

    # If saved_zoom exists, use it (respects user's saved zoom or previously calculated zoom)
    if self.controls.saved_zoom is not None:
      return self.controls.saved_zoom

    # Calculate the combined ranges from both projections and gold standard
    proj_x_min, proj_x_max, proj_y_min, proj_y_max = (
      self._calculate_initial_ranges_from_projections(df)
    )
    gs_x_min, gs_x_max, gs_y_min, gs_y_max = self._calculate_initial_ranges_from_gold_standard(
      gold_std_df
    )
    x_min = self._take_valid_min(proj_x_min, gs_x_min)
    x_max = self._take_valid_max(proj_x_max, gs_x_max)
    y_min = self._take_valid_min(proj_y_min, gs_y_min)
    y_max = self._take_valid_max(proj_y_max, gs_y_max)

    # Set saved_zoom to combined calculated values if we have valid ranges
    # This ensures saved_zoom includes both projections and gold standard data
    if x_min is not None and x_max is not None and y_min is not None and y_max is not None:
      y_range_span = y_max - y_min
      y_max_with_padding = y_max + (y_range_span * 0.02)
      combined_zoom = Zoom(x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max_with_padding)
      self.controls.saved_zoom = combined_zoom
      return combined_zoom

    return Zoom(x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)

  def _calculate_initial_ranges_from_projections(
    self, df: pd.DataFrame
  ) -> tuple[float | datetime | None, float | datetime | None, float | None, float | None]:
    x_min = None
    x_max = None
    y_min = None
    y_max = None

    # Calculate initial X and Y axis ranges using scenario data and uncertainty intervals (if any)
    for scenario in self.controls.scenarios:
      scenario_df = df.query('scenario_id == @scenario.id')
      if not scenario_df.empty:
        # X axis range will be the same for all models in the scenario
        x_min, x_max = self.calculate_new_x_range(scenario_df, x_min, x_max)

        for model in self.controls.models:
          model_data = scenario_df.query('type_id == 0.5 and model_name == @model.id')
          if not model_data.empty:
            if self.controls.uncertainty_interval is not None:
              for lower_q, upper_q in self.controls.uncertainty_interval.get_bounds():
                lower_model_data = scenario_df.query(
                  'type_id == @lower_q and model_name == @model.id'
                )
                upper_model_data = scenario_df.query(
                  'type_id == @upper_q and model_name == @model.id'
                )
                if not lower_model_data.empty:
                  y_min, y_max = self.calculate_new_y_range(lower_model_data, y_min, y_max)
                if not upper_model_data.empty:
                  y_min, y_max = self.calculate_new_y_range(upper_model_data, y_min, y_max)
            else:
              y_min, y_max = self.calculate_new_y_range(model_data, y_min, y_max)
    return x_min, x_max, y_min, y_max

  def _calculate_initial_ranges_from_gold_standard(
    self, gold_std_df: pd.DataFrame
  ) -> tuple[float | None, float | None, float | None, float | None]:
    """Calculate the initial X and Y axis ranges for all subplots in the chart from the gold standard data."""
    x_min = None
    x_max = None
    y_min = None
    y_max = None

    if not gold_std_df.empty:
      x_min, x_max = self.calculate_new_x_range(gold_std_df, x_min, x_max)
      y_min, y_max = self.calculate_new_y_range(gold_std_df, y_min, y_max)

    return x_min, x_max, y_min, y_max

  def _plot_primary_line(self, scenario_df: pd.DataFrame, model: Model, row_num: int):
    primary_line_data = scenario_df.query('type_id == 0.5 and model_name == @model.id')
    self._fig.add_trace(
      go.Scatter(
        x=primary_line_data.index,
        y=primary_line_data[self.controls.y_axis],
        mode='lines',
        name=f'Model {model.name}',
        legendgroup=f'Model {model.name}',
        showlegend=(row_num == 1),
        line=dict(color=model.color),
      ),
      row=row_num,
      col=1,
    )

  def _plot_gold_standard_line(self, gold_std_df: pd.DataFrame, row_num: int):
    self._fig.add_trace(
      go.Scatter(
        x=gold_std_df.index,
        y=gold_std_df['value'],
        mode='lines+markers',
        name='Gold standard',
        line=dict(color='#999', dash='solid', width=1),
        marker=dict(color='var(--mantine-color-text)', symbol='diamond'),
        legendgroup='Gold standard',
        showlegend=(row_num == 1),
      ),
      row=row_num,
      col=1,
    )

  def get_fig(self) -> go.Figure:
    return self._fig

  def get_raw_dataframe(self) -> pd.DataFrame:
    return self._raw_df

  def get_title(self) -> str:
    return f'{self.controls.target.display_value} Over Time'

  def get_subtitle(self) -> str:
    return (
      f'Location: {self.controls.location.name}'
      + f' | Age group: {self.controls.age_group.display_value}'
      + (
        f' | Uncertainty interval: {self.controls.uncertainty_interval.display_value}'
        if self.controls.uncertainty_interval
        else ''
      )
    )

  def update_controls(self, controls: ChartControls) -> None:
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
    new_raw_df[self.controls.x_axis] = pd.to_datetime(new_raw_df[self.controls.x_axis])
    new_raw_df = new_raw_df.set_index(self.controls.x_axis)
    self._raw_df = new_raw_df

  def update_uncertainty_interval(self, uncertainty_interval: str | None):
    """
    Update the uncertainty interval.
    """
    self.controls.uncertainty_interval = (
      UncertaintyInterval.from_display_value(uncertainty_interval) if uncertainty_interval else None
    )
    self.refresh_fig()

  def _plot_uncertainty_interval(self, scenario_df: pd.DataFrame, model: Model, row_num: int):
    if (
      self.controls.uncertainty_interval is None
      or self.controls.uncertainty_interval == UncertaintyInterval.NONE
    ):
      return
    for lower_q, upper_q in self.controls.uncertainty_interval.get_bounds():
      lower_model = scenario_df.query('type_id == @lower_q and model_name == @model.id')
      upper_model = scenario_df.query('type_id == @upper_q and model_name == @model.id')
      fill_color = get_model_color_with_uncertainty_interval(
        model.color,
        uncertainty_interval=UncertaintyInterval.from_bounds([(lower_q, upper_q)]),
      )
      self._fig.add_trace(
        go.Scatter(
          x=pd.concat([lower_model.index.to_series(), upper_model.index.to_series()[::-1]]),
          y=pd.concat([lower_model[self.controls.y_axis], upper_model[self.controls.y_axis][::-1]]),
          fill='toself',
          fillcolor=fill_color,
          line=dict(color='rgba(0,0,0,0)'),
          legendgroup=f'Model {model.name}',
          hoverinfo='skip',
          showlegend=False,
        ),
        row=row_num,
        col=1,
      )

  def _reload_data(self):
    """
    Reload data, for example if a variable changed, e.g. round number, location, target, etc.
    This is called by individual update methods when data-dependent fields change.
    """
    new_raw_df = Chart.collect_data(
      self.controls.data_type,
      self.controls.round_num,
      self.controls.location.name,
      self.controls.target.input_value,
    )
    new_raw_df[self.controls.x_axis] = pd.to_datetime(new_raw_df[self.controls.x_axis])
    new_raw_df = new_raw_df.set_index(self.controls.x_axis)
    self._raw_df = new_raw_df
