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
    num_cols = 2
    self._fig = make_subplots(
      rows=num_rows,
      cols=num_cols,
      vertical_spacing=0.1,
      specs=[[{'secondary_y': False}, {'secondary_y': True}] for _ in range(num_rows)],
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
      self._fig.add_trace(
        go.Box(
          x=scenario_df[self.controls.x_axis],
          marker_color=get_model_color_by_id(ensemble_model_id),
        )
        if self.controls.x_axis
        else go.Box(
          y=scenario_df[self.controls.y_axis],
          marker_color=get_model_color_by_id(ensemble_model_id),
        ),
        row=i,
        col=1,
      )
      self._fig.add_trace(
        go.Box(
          x=scenario_df[self.controls.x_axis],
          marker_color=get_model_color_by_id(ensemble_model_id),
        )
        if self.controls.x_axis
        else go.Box(
          y=scenario_df[self.controls.y_axis],
          marker_color=get_model_color_by_id(ensemble_model_id),
        ),
        row=i,
        col=2,
        secondary_y=True,
      )

    # plot annotations
    self._plot_annotations()

    # update axes so that they use a secondary y-axis only for the second column
    self._fig.update_xaxes(showspikes=True, spikemode='across', spikesnap='cursor')
    for row in range(1, num_rows + 1):
      # Update primary y-axis for first column
      self._fig.update_yaxes(
        showspikes=True,
        spikemode='across',
        row=row,
        col=1,
        title_text=None,
      )

      # Update secondary y-axis for second column with dynamic title
      y_axis_title = f'Scenario {self.controls.scenarios[row - 1].name}'
      self._fig.update_yaxes(
        showspikes=True,
        spikemode='across',
        row=row,
        col=2,
        title_text=y_axis_title,
        secondary_y=True,
      )

    # update zoom ranges
    if (
      self.controls.zoom is not None
      and self.controls.zoom.x is not None
      and self.controls.zoom.x.get('min') is not None
      and self.controls.zoom.x.get('max') is not None
    ):
      self._fig.update_xaxes(
        range=[self.controls.zoom.x.get('min'), self.controls.zoom.x.get('max')]
      )
    if (
      self.controls.zoom is not None
      and self.controls.zoom.y is not None
      and self.controls.zoom.y.get('min') is not None
      and self.controls.zoom.y.get('max') is not None
    ):
      self._fig.update_yaxes(
        range=[self.controls.zoom.y.get('min'), self.controls.zoom.y.get('max')]
      )

    self._fig.update_layout(
      hovermode='closest',
      height=400 + (200 * max(0, num_rows - 1)),
      title='Forecast distribution (boxplot)',
      uirevision=self.__hash__(),
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
