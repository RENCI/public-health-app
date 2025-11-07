import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.components.chart.chart import Chart
from src.components.chart.chart_controls import ChartControls
from src.components.enums import CertaintyInterval
from src.constants import get_model_color_by_id, get_model_id


class BoxplotChart(Chart):
  """Chart class for displaying boxplot visualizations"""

  def __init__(self, controls: ChartControls):
    super().__init__(controls)
    self._raw_df = Chart.collect_data(
      self.controls.data_type,
      self.controls.round_num,
      self.controls.location.name,
      'incident_hospitalization',
    )
    # self._second_raw_df = Chart.collect_data(
    #   self.controls.data_type,
    #   self.controls.round_num,
    #   self.controls.location.name,
    #   'incident_death',
    # )
    self._fig = go.Figure()

    self.refresh_fig()

  def __hash__(self):
    """
    Generate a unique hash for chart instances based on their parameters.
    This creates a deterministic string representation that can be used as a key.
    """
    return hash(self.get_key(self.controls))

  def __eq__(self, other):
    return isinstance(other, BoxplotChart) and self.controls == other.controls

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
    # second_df = self._second_raw_df
    # filter for given age group
    df = df.query('age_group == @self.controls.age_group.input_value')
    # second_df = second_df.query('age_group == @self.controls.age_group.input_value')
    # filter for ensemble model, specifically
    ensemble_model_id = get_model_id('Ensemble')
    df = df.query('model_name == @ensemble_model_id')
    # second_df = second_df.query('model_name == @ensemble_model_id')

    for i, scenario in enumerate(self.controls.scenarios, start=1):
      scenario_df = df.query('scenario_id == @scenario.id')
      # second_scenario_df = second_df.query('scenario_id == @scenario.id')
      scenario_display_name = f'Scenario {scenario.name.split()[0][0].upper()}'
      trace = go.Box(
        marker_color=get_model_color_by_id(ensemble_model_id),
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
      # Get the axis domain for this subplot
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
      self._fig.add_annotation(
        text=scenario_display_name,
        xref='paper',
        yref='paper',
        x=x_paper,
        y=y_paper,
        xanchor='left',
        yanchor='middle',
        textangle=-90,
        showarrow=False,
        font=dict(size=12),
      )

    # plot annotations
    self._plot_annotations()

    # update axes
    self._fig.update_xaxes(showspikes=False)
    self._fig.update_yaxes(showspikes=False)

    # calculate global x-axis range across all scenarios
    should_use_zoom = (
      self.controls.zoom is not None
      and self.controls.zoom.x is not None
      and self.controls.zoom.x.get('min') is not None
      and self.controls.zoom.x.get('max') is not None
      and self.controls.zoom.y is not None
      and self.controls.zoom.y.get('min') is not None
      and self.controls.zoom.y.get('max') is not None
    )
    if self.controls.x_axis and not should_use_zoom:
      for scenario in self.controls.scenarios:
        scenario_df = df.query('scenario_id == @scenario.id')
        scenario_x_values = scenario_df[self.controls.x_axis]
        if scenario_x_values.empty:
          continue
        x_min = scenario_x_values.min()
        x_max = scenario_x_values.max()
        if x_min is not None and x_max is not None and (x_min < x_max):
          self._fig.update_xaxes(range=[x_min, x_max])
          break
    elif self.controls.y_axis and not should_use_zoom:
      for scenario in self.controls.scenarios:
        scenario_df = df.query('scenario_id == @scenario.id')
        scenario_y_values = scenario_df[self.controls.y_axis]
        if scenario_y_values.empty:
          continue
        y_min = scenario_y_values.min()
        y_max = scenario_y_values.max()
        if y_min is not None and y_max is not None and (y_min < y_max):
          self._fig.update_yaxes(range=[y_min, y_max])
          break
    elif should_use_zoom:
      self._fig.update_xaxes(
        range=[self.controls.zoom.x.get('min'), self.controls.zoom.x.get('max')]
      )
      self._fig.update_yaxes(
        range=[self.controls.zoom.y.get('min'), self.controls.zoom.y.get('max')]
      )

    self._fig.update_layout(
      hovermode='closest',
      height=400 + (200 * max(0, num_rows - 1)),
      title='Forecast distribution (boxplot)',
      uirevision=self.__hash__(),
      showlegend=False,
    )

    self.set_theme()

    return self._fig

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
    self._raw_df = new_raw_df

  def update_certainty_percent(self, certainty_percent: str | None):
    """
    Update the certainty percentage.
    """
    self.controls.certainty_percent = (
      CertaintyInterval.from_display_value(certainty_percent) if certainty_percent else None
    )
    self.refresh_fig()
