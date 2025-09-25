from enum import StrEnum
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.components.enums import AgeGroup, DataType, Target
from src.constants import (
  get_locations,
  get_model_color,
  get_model_id,
  get_model_name,
  get_scenario_name,
)

BASE_DATA_DIR = Path(__file__).resolve().parent.parent / 'data'
FIFTY_PERCENT = '50%'
NINETY_FIVE_PERCENT = '95%'
MULTI = 'Multi'
# mapping confidence interval value to quantile bounds
conf_int_map = {
  FIFTY_PERCENT: [(0.25, 0.75)],
  NINETY_FIVE_PERCENT: [(0.025, 0.975)],
  MULTI: [(0.025, 0.975), (0.05, 0.95), (0.1, 0.9), (0.25, 0.75)],
}
conf_int_colors = {
  (0.025, 0.975): 'rgba(200,200,255,0.2)',  # lightest
  (0.05, 0.95): 'rgba(150,150,255,0.3)',
  (0.1, 0.9): 'rgba(100,100,255,0.4)',
  (0.25, 0.75): 'rgba(50,50,255,0.6)',  # darkest
}


class Scenario:
  def __init__(self, scenario_id: int):
    self.id = scenario_id
    self.name = get_scenario_name(scenario_id)
    self.variables = ['']  # TODO: add variables

  def __str__(self):
    return f'{self.name}'


class Model:
  def __init__(self, model_id_or_name: int | str):
    if isinstance(model_id_or_name, int):
      self.id = model_id_or_name
      self.name = get_model_name(self.id)
    else:
      self.id = get_model_id(model_id_or_name)
      self.name = model_id_or_name
    self.color = get_model_color(self.id)

  def __str__(self):
    return f'{self.name}'


class Location:
  def __init__(self, location_name: str):
    if location_name.upper() == 'US':
      self.name = location_name.upper()
    else:
      self.name = location_name.lower().capitalize()
    location_data = get_locations()[self.name]
    self.short_code, self.index, self.population = location_data

  def __str__(self):
    return f'{self.name}'


class Annotation:
  def __init__(self, value: float, label: str, color: str):
    self.value = value
    self.label = label
    self.color = color


class HorizontalAnnotation(Annotation):
  def __init__(self, value: float, label: str, color: str):
    super().__init__(value, label, color)


class VerticalAnnotation(Annotation):
  def __init__(self, value: float, label: str, color: str):
    super().__init__(value, label, color)


class PlotTitle:
  def __init__(
    self,
    pathogen: str,
    scenario: Scenario,
    models: list[Model],
    location: Location,
    age_group: AgeGroup | None,
  ):
    self.pathogen = pathogen
    self.scenario = scenario
    self.location = location
    self.age_group = age_group
    if not age_group:
      self.age_group = AgeGroup.ALL

  def __str__(self):
    return (
      f'{self.pathogen} Scenario {self.scenario}'
      + f'{(self.age_group.display_value + " ") if self.age_group else ""} in {self.location}'
    )


class PlotType(StrEnum):
  LINE = 'line'
  BOXPLOT = 'boxplot'


class ChartControls:
  def __init__(
    self,
    x_axis: str,
    y_axis: str,
    round_num: int,
    pathogen: str,
    scenario_ids: list[int],
    model_ids: list[int],
    location_name: str,
    target: str,
    age_group: str | None = None,
    annotations: list[dict[str, Any]] | None = None,
    certainty_percent: str | None = None,
  ):
    self.x_axis = x_axis
    self.y_axis = y_axis
    self.round_num = round_num
    self.pathogen = pathogen
    self.scenarios = [Scenario(scenario_id) for scenario_id in scenario_ids]
    self.models = [Model(model_id) for model_id in model_ids]
    self.location = Location(location_name)
    self.target = Target(target)
    self.age_group = AgeGroup.from_input_value(age_group) if age_group else None
    self.annotations = (
      [Annotation(**annotation) for annotation in annotations] if annotations else []
    )
    self.certainty_percent = int(certainty_percent.strip('%')) if certainty_percent else None


class Chart:
  def __init__(self, plot_type: PlotType, controls: ChartControls):
    self.plot_type = plot_type
    self.controls = controls
    self.scenarios = controls.scenarios
    self._data_type = DataType.QUANTILE
    self._raw_df = self.collect_data(
      self._data_type, self.controls.round_num, self.controls.location, self.controls.target
    )
    self._raw_df = self._raw_df.set_index(self.controls.x_axis)
    self._fig: go.Figure = go.Figure()

    # Public so that it can be accessed and modified by the viz editor
    self.annotations: list[Annotation] = controls.annotations or []

    self.refresh_fig()

  def refresh_fig(self) -> go.Figure:
    if not self.controls.scenarios:
      raise ValueError('Scenario is required to display chart.')
    if not self.controls.models:
      raise ValueError('Models are required to display chart.')

    df = self._raw_df.sort_values(by=self.controls.x_axis)

    if self.plot_type == PlotType.LINE:
      self._fig = px.line(df, y=self.controls.y_axis)
    elif self.plot_type == PlotType.BOXPLOT:
      self._fig = px.box(df, y=self.controls.y_axis)
    else:
      raise ValueError(f'Invalid chart type: {self.plot_type}')
    for annotation in self.annotations:
      self._fig.add_annotation(
        x=annotation.value if isinstance(annotation, HorizontalAnnotation) else None,
        y=annotation.value if isinstance(annotation, VerticalAnnotation) else None,
        text=annotation.label,
        showarrow=False,
        font=dict(color=annotation.color),
      )

    # load gold standard data (the actual data up to present day, not projections)
    gold_std_df = self.collect_gold_std_data(
      self.controls.round_num, self.controls.location, self.controls.target
    )
    scenario_ids = [scenario.id for scenario in self.controls.scenarios]
    model_names = [model.name for model in self.controls.models]
    df = df.query('scenario_id.isin(@scenario_ids)')
    df = df.query('model_name.isin(@model_names)')
    df = df.query('age_group == @self.controls.age_group.input_value')
    df = df.query('location == @self.controls.location.name')

    num_rows = len(self.controls.scenarios)
    self._fig = make_subplots(
      rows=num_rows,
      cols=1,
      vertical_spacing=0.1,
      subplot_titles=[f'Scenario {s}' for s in self.controls.scenarios],
    )
    self._fig.update_xaxes(matches='x')
    self._fig.update_yaxes(matches='y')

    for i, _ in enumerate(self.controls.scenarios, start=1):
      scenario_df = df.query('scenario_id == @scenario.id')

      # main line for median (0.5 quantile)
      median_df = scenario_df.query('type_id == 0.5')
      for model_name in median_df['model_name'].unique():
        model_df = median_df.query('model_name == @model_name')
        self._fig.add_trace(
          go.Scatter(
            x=model_df['horizon'],
            y=model_df['value'],
            mode='lines+markers',
            name=f'Model {model_name}',
            legendgroup=f'Model {model_name}',
            showlegend=(i == 1),
          ),
          row=i,
          col=1,
        )

      # add uncertainty intervals
      if self.controls.certainty_percent in conf_int_map:
        for lower_q, upper_q in conf_int_map[self.controls.certainty_percent]:
          lower = scenario_df.query('type_id == @lower_q')
          upper = scenario_df.query('type_id == @upper_q')

          for model_name in lower['model_name'].unique():
            lower_model = lower.query('model_name == @model_name')
            upper_model = upper.query('model_name == @model_name')

            self._fig.add_trace(
              go.Scatter(
                x=pd.concat([lower_model['horizon'], upper_model['horizon'][::-1]]),
                y=pd.concat([lower_model['value'], upper_model['value'][::-1]]),
                fill='toself',
                fillcolor=conf_int_colors[(lower_q, upper_q)],
                line=dict(color='rgba(0,0,0,0)'),
                hoverinfo='skip',
                showlegend=False,
              ),
              row=i,
              col=1,
            )

      # gold standard line
      self._fig.add_trace(
        go.Scatter(
          x=gold_std_df['time_value'],
          y=gold_std_df['value'],
          mode='lines+markers',
          name='Gold standard',
          line=dict(color='rebeccapurple', dash='dot'),
          marker=dict(symbol='diamond'),
          legendgroup='Gold standard',
          showlegend=(i == 1),
        ),
        row=i,
        col=1,
      )

    for annotation in self.annotations:
      if isinstance(annotation, HorizontalAnnotation):
        for _ in self._fig.select_yaxes():
          self._fig.add_hline(
            y=annotation.value,
            line_dash='dot',
            line_color=annotation.color,
            line_width=1,
            annotation_text=annotation.label,
            annotation_font_color=annotation.color,
          )

      elif isinstance(annotation, VerticalAnnotation):
        for _ in self._fig.select_xaxes():
          self._fig.add_vline(
            x=annotation.value,
            line_dash='dot',
            line_color=annotation.color,
            line_width=1,
            annotation_text=annotation.label,
            annotation_font_color=annotation.color,
          )

    self._fig.update_layout(
      hovermode='x unified', height=300 * num_rows, title='Forecast values over time (by scenario)'
    )
    self._fig.update_xaxes(showspikes=True, spikemode='across', spikesnap='cursor')
    self._fig.update_yaxes(showspikes=True, spikemode='across')

    return self._fig

  def get_controls(self) -> ChartControls:
    return self.controls

  def get_fig(self) -> go.Figure:
    return self._fig

  def get_data(self) -> pd.DataFrame:
    return self._raw_df

  def _build_dataset_path(
    self,
    *,
    data_type: DataType = DataType.QUANTILE,
    round_number: int = 1,
    location: Location = Location('US'),
    target: Target = Target.INCIDENT_HOSPITALIZATION,
    part: int = 0,
  ) -> Path:
    part = str(part)
    round_fragment = f'round{round_number}'
    path = (
      BASE_DATA_DIR
      / round_fragment
      / str(target)
      / location.name
      / data_type.get_path_value()
      / f'part-{part}.{data_type.get_file_extension()}'
    )
    if not path.exists() or not path.is_file():
      raise FileNotFoundError(f'File not found for chart: {path}')
    return path

  def collect_data(
    self,
    data_type: DataType = DataType.QUANTILE,
    round_number: int = 1,
    location: Location = Location('US'),
    target: Target = Target.INCIDENT_HOSPITALIZATION,
    part: int = 0,
  ) -> pd.DataFrame:
    path = self._build_dataset_path(
      data_type=data_type,
      round_number=round_number,
      location=location,
      target=target,
      part=part,
    )
    if not path.exists() or not path.is_file():
      raise FileNotFoundError(f'File not found for chart: {path}')

    try:
      if data_type == DataType.QUANTILE and path.suffix == '.csv':
        df = pd.read_csv(path, engine='pyarrow')
      elif data_type == DataType.SAMPLE and path.suffix == '.parquet':
        df = pd.read_parquet(path, engine='pyarrow')
      else:
        raise ValueError(
          f'Path file extension {path.suffix} does not match expected file extension'
          + f' {data_type.get_file_extension()} for data type: {data_type}'
        )
      return df
    except Exception as e:
      print(f'Error reading file "{path}": {e}')
      raise e

  def _build_gold_std_path(self, round_number: int, location: Location, target: Target) -> Path:
    return BASE_DATA_DIR / f'round{round_number}' / 'gold_standard' / 'covid_nhsn_hosp_inc.csv'

  def collect_gold_std_data(
    self,
    round_number: int,
    location: Location,
    target: Target,
  ) -> pd.DataFrame:
    gold_std_path = self._build_gold_std_path(round_number, location, target)
    if not gold_std_path.exists() or not gold_std_path.is_file():
      raise FileNotFoundError(f'File not found for gold standard data: {gold_std_path}')
    return pd.read_csv(gold_std_path, parse_dates=['time_value'])
