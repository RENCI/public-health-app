import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.components.chart.chart import Chart
from src.components.chart.chart_controls import ChartControls
from src.components.chart.chart_properties import Model
from src.components.enums import ChartLayout, UncertaintyInterval
from src.util.constants import get_model_color_with_uncertainty_interval


class LineChart(Chart):
  """Chart class for displaying a chart"""

  def __init__(self, controls: ChartControls):
    super().__init__(controls)
    self._raw_df[self.controls.x_axis] = pd.to_datetime(self._raw_df[self.controls.x_axis])
    self._raw_df = self._raw_df.set_index(self.controls.x_axis)

    self.refresh_fig()

  def __hash__(self):
    """
    Generate a unique hash for chart instances based on their parameters.
    This creates a deterministic string representation that can be used as a key.
    """
    return hash(self.get_key(self.controls))

  def __eq__(self, other):
    return isinstance(other, LineChart) and self.controls == other.controls

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

    # update layout
    num_scenarios = len(self.controls.scenarios)

    if self.controls.chart_layout == ChartLayout.STACK:
      num_cols = 1
    elif self.controls.chart_layout == ChartLayout.GRID:
      num_cols = 2

    num_rows = (num_scenarios + num_cols - 1) // num_cols

    # Define fixed dimensions
    SUBPLOT_HEIGHT = 250  # Fixed height per subplot in pixels
    FIXED_SPACING = 100  # Fixed spacing between subplots in pixels

    # Calculate total figure height accounting for fixed spacing
    chart_total_height = (SUBPLOT_HEIGHT * num_rows) + (FIXED_SPACING * (num_rows - 1)) + 180

    # Calculate vertical_spacing as a fraction of total height
    # This ensures the actual pixel spacing remains constant
    if num_rows > 1:
      vertical_spacing = FIXED_SPACING / chart_total_height
    else:
      vertical_spacing = 0  # No spacing needed for single subplot

    # start with the raw dataframe
    df = self._raw_df

    # filter for given age group
    df = df.query('age_group == @self.controls.age_group.input_value')

    # load gold standard data once (same for all scenarios)
    gold_std_df = Chart.collect_gold_std_data(self.controls.round_num)
    gold_std_df['time_value'] = pd.to_datetime(gold_std_df['time_value'])
    gold_std_df = gold_std_df.set_index('time_value')
    gold_std_df = gold_std_df.query('age_group == @self.controls.age_group.input_value')
    gold_std_df = gold_std_df.query('geo_value_fullname == @self.controls.location.name')
    gold_std_df = gold_std_df.loc[self.controls.x_start_date or gold_std_df.index.min() :]

    # create subplots
    self._fig = make_subplots(
      rows=num_rows,
      cols=num_cols,
      vertical_spacing=vertical_spacing,
      row_heights=[1] * num_rows,
      subplot_titles=[f'{s.name.split("-")[0]}. {s.description}' for s in self.controls.scenarios],
      shared_xaxes=True,
      shared_yaxes=True,
    )

    # add traces for each scenario
    for i, scenario in enumerate(self.controls.scenarios, start=1):
      current_row = (i - 1) // num_cols + 1
      current_col = (i - 1) % num_cols + 1

      # filter for given scenario
      scenario_df = df.query('scenario_id == @scenario.id')

      # decide whether to add uncertainty intervals
      should_add_uncertainty_intervals = self.controls.uncertainty_interval is not UncertaintyInterval.NONE

      # add traces for each model
      for model in self.controls.models:
        # add uncertainty intervals if necessary
        if should_add_uncertainty_intervals:
          self._plot_uncertainty_interval(
            scenario_df=scenario_df,
            model=model,
            row_num=current_row,
            col_num=current_col,
          )
        else:
          # add main line (0.5 quantile)
          primary_line_data = scenario_df.query('type_id == 0.5 and model_name == @model.id')
          self._fig.add_trace(
            go.Scatter(
              x=primary_line_data.index,
              y=primary_line_data[self.controls.y_axis],
              mode='lines',
              name=f'{model.name}',
              legendgroup=f'{model.name}',
              showlegend=(i == 1),
              line=dict(color=model.color),
            ),
            row=current_row,
            col=current_col,
          )

      # add gold standard line
      self._fig.add_trace(
        go.Scatter(
          x=gold_std_df.index,
          y=gold_std_df['value'],
          mode='lines+markers',
          name='Actual',
          line=dict(color='#999', dash='solid', width=1),
          marker=dict(color='var(--mantine-color-text)', symbol='diamond'),
          legendgroup='Actual',
          showlegend=(i == 1),
        ),
        row=current_row,
        col=current_col,
      )

    # plot annotations
    self._plot_annotations()

    # reduce the font size of the subplot titles,
    # which are treated as annotations by plotly.
    for annotation in self._fig.layout.annotations:
      annotation['font'] = dict(size=12)

    # apply spike guides for each axis in the chart viewport
    self._fig.update_xaxes(showspikes=True, spikemode='across', spikesnap='cursor')
    self._fig.update_yaxes(showspikes=True, spikemode='across')

    # calculate global min/max across all subplots for synchronized axes
    has_zoom = (
      self.controls.zoom is not None
      and self.controls.zoom.x is not None
      and self.controls.zoom.x.get('min') is not None
      and self.controls.zoom.x.get('max') is not None
      and self.controls.zoom.y is not None
      and self.controls.zoom.y.get('min') is not None
      and self.controls.zoom.y.get('max') is not None
    )

    if has_zoom:
      x_range = [self.controls.zoom.x.get('min'), self.controls.zoom.x.get('max')]
      y_range = [self.controls.zoom.y.get('min'), self.controls.zoom.y.get('max')]
    else:
      x_min = None
      x_max = None
      y_min = None
      y_max = None

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
      else:
        x_range = None
        y_range = None

    if x_range is not None and y_range is not None:
      for r in range(1, num_rows + 1):
        for c in range(1, num_cols + 1):
          self._fig.update_xaxes(range=x_range, row=r, col=c)
          self._fig.update_yaxes(range=y_range, row=r, col=c)

    self._fig.update_yaxes(title_text=self.controls.target.display_value)

    self._fig.update_layout(
      hovermode='x unified',
      height=chart_total_height,
      title=dict(
        text=self.get_title(),
        x=0.5,
        y=1,
        xref='container',
        xanchor='center',
        yanchor='top',
        font=dict(size=28),
        pad=dict(t=35, r=0, b=0, l=0),
        subtitle=dict(
          text=self.get_subtitle(),
          font=dict(size=16),
        ),
      ),
      margin=dict(t=144, r=48, b=48, l=48),
      uirevision=self.__hash__(),
    )

    self.set_theme()

    return self._fig

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
      self.controls.data_type,
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

  def _plot_uncertainty_interval(self, scenario_df: pd.DataFrame, model: Model, row_num: int, col_num: int):
    all_bounds = self.controls.uncertainty_interval.get_bounds()
    for i, bounds in enumerate(all_bounds):
      lower_q, upper_q = bounds
      lower_model = scenario_df.query('type_id == @lower_q and model_name == @model.id')
      upper_model = scenario_df.query('type_id == @upper_q and model_name == @model.id')
      fill_color = get_model_color_with_uncertainty_interval(
        model.color,
        uncertainty_interval=UncertaintyInterval.from_bounds([(lower_q, upper_q)]),
        use_varying_opacity=self.controls.uncertainty_interval==UncertaintyInterval.ALL,
      )
      self._fig.add_trace(
        go.Scatter(
          x=pd.concat([lower_model.index.to_series(), upper_model.index.to_series()[::-1]]),
          y=pd.concat([lower_model[self.controls.y_axis], upper_model[self.controls.y_axis][::-1]]),
          fill='toself',
          fillcolor=fill_color,
          line=dict(color='rgba(0,0,0,0)'),
          name=f'{model.name}',
          legendgroup=f'{model.name}',
          hoverinfo='skip',
          showlegend=(row_num == 1 and col_num == 1 and i == len(all_bounds) - 1),
        ),
        row=row_num,
        col=col_num,
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
