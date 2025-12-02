import copy

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.components.chart.chart import Chart
from src.components.chart.chart_controls import ChartControls
from src.components.chart.chart_properties import DatetimeAxisRange, FloatAxisRange, Model
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
    self._set_axes_ranges(df, self._gold_std_df, num_rows)

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

  def _set_axes_ranges(self, df: pd.DataFrame, gold_std_df: pd.DataFrame, num_rows: int):
    x_range, y_range = self._calculate_axes_ranges(df, gold_std_df)
    if x_range is not None and y_range is not None:
      for i in range(1, num_rows + 1):
        self._fig.update_xaxes(range=[x_range.min, x_range.max], row=i, col=1)
        self._fig.update_yaxes(range=[y_range.min, y_range.max], row=i, col=1)

  def _calculate_axes_ranges(
    self, df: pd.DataFrame, gold_std_df: pd.DataFrame
  ) -> tuple[DatetimeAxisRange | None, FloatAxisRange | None]:
    """
    Calculate the x and y axis ranges for all subplots in the chart.
    Zoom logic:
      * If current_zoom is set in the controls, use it
      * If saved_zoom is set in the controls but not current_zoom, set current_zoom to saved_zoom and use it
      * If neither current_zoom nor saved_zoom is set, calculate the ranges from the data, then
        set both zooms to the calculated ranges
      * If the Use Chart Zoom button is pressed, set both zooms to the current axis values
      * If the zoom is manually changed through either the chart or the controls, do not change saved_zoom, only current_zoom
      * If the insight is saved, set saved_zoom to current_zoom
    """
    if self.controls.current_zoom is not None:
      x_range = self.controls.current_zoom.x
      y_range = self.controls.current_zoom.y
      return x_range, y_range

    if self.controls.saved_zoom is not None:
      # Set current_zoom to saved_zoom for first load
      self.controls.current_zoom = copy.deepcopy(self.controls.saved_zoom)
      x_range = self.controls.saved_zoom.x
      y_range = self.controls.saved_zoom.y
      return x_range, y_range

    x_min = None
    x_max = None
    y_min = None
    y_max = None
    x_range = None
    y_range = None

    # calculate x and y axis ranges from data
    for scenario in self.controls.scenarios:
      scenario_df = df.query('scenario_id == @scenario.id')
      if not scenario_df.empty:
        scenario_x_values = scenario_df.index
        if x_min is None or scenario_x_values.min() < x_min:
          x_min = scenario_x_values.min()
        if x_max is None or scenario_x_values.max() > x_max:
          x_max = scenario_x_values.max()

        for model in self.controls.models:
          model_data = scenario_df.query('type_id == 0.5 and model_name == @model.id')
          if not model_data.empty:
            model_y_values = model_data[self.controls.y_axis]
            if y_min is None or model_y_values.min() < y_min:
              y_min = model_y_values.min()
            if y_max is None or model_y_values.max() > y_max:
              y_max = model_y_values.max()

          if self.controls.uncertainty_interval is not None:
            for lower_q, upper_q in self.controls.uncertainty_interval.get_bounds():
              lower_model_data = scenario_df.query(
                'type_id == @lower_q and model_name == @model.id'
              )
              upper_model_data = scenario_df.query(
                'type_id == @upper_q and model_name == @model.id'
              )
              if not lower_model_data.empty:
                lower_y_values = lower_model_data[self.controls.y_axis]
                if y_min is None or lower_y_values.min() < y_min:
                  y_min = lower_y_values.min()
              if not upper_model_data.empty:
                upper_y_values = upper_model_data[self.controls.y_axis]
                if y_max is None or upper_y_values.max() > y_max:
                  y_max = upper_y_values.max()

    if not gold_std_df.empty:
      gold_std_x_values = gold_std_df.index
      if x_min is None or gold_std_x_values.min() < x_min:
        x_min = gold_std_x_values.min()
      if x_max is None or gold_std_x_values.max() > x_max:
        x_max = gold_std_x_values.max()

      gold_std_y_values = gold_std_df['value']
      if y_min is None or gold_std_y_values.min() < y_min:
        y_min = gold_std_y_values.min()
      if y_max is None or gold_std_y_values.max() > y_max:
        y_max = gold_std_y_values.max()

    if x_min is not None and x_max is not None and y_min is not None and y_max is not None:
      x_range = [x_min, x_max]
      y_range = [y_min, y_max]
      y_range_span = y_max - y_min
      y_range[1] = y_max + (y_range_span * 0.02)
      # Set current_zoom and saved_zoom to calculated values
      from src.components.chart.chart_properties import Zoom

      zoom = Zoom(x_min=x_range[0], x_max=x_range[1], y_min=y_range[0], y_max=y_range[1])
      self.controls.current_zoom = zoom
      self.controls.saved_zoom = zoom
      return zoom.x, zoom.y
    return None, None

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
