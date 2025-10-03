from datetime import datetime
from abc import ABC
from dataclasses import asdict
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Any, Self

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.components.enums import AgeGroup, DataType, Target, Uncertainty
from src.constants import (
  get_locations,
  get_model_color,
  get_model_id,
  get_model_name,
  get_scenario_id,
  get_scenario_name,
)

BASE_DATA_DIR = Path(__file__).resolve().parent.parent / 'data' / 'rounds'
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
  def __init__(self, id: int | None = None, name: str | None = None):
    if id:
      self.id = id
      self.name = get_scenario_name(id)
    elif name:
      self.id = get_scenario_id(name)
      self.name = name
    else:
      raise ValueError('Scenario must be initialized with either scenario_id or scenario_name')
    self.variables = ['']  # TODO: add variables

  def __str__(self):
    return f'{self.name}'

  def __hash__(self):
    return hash(self.name)

  def __eq__(self, other):
    return isinstance(other, Scenario) and self.name == other.name


class Model:
  def __init__(self, model_id_or_name: int | str):
    if isinstance(model_id_or_name, int):
      self.id = model_id_or_name
      self.name = get_model_name(self.id)
    else:
      self.id = get_model_id(model_id_or_name)
      self.name = model_id_or_name
    self.color = get_model_color(self.id)

  def __hash__(self):
    return hash(self.name)

  def __eq__(self, other):
    return isinstance(other, Model) and self.name == other.name


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

  def __hash__(self):
    return hash(self.name)

  def __eq__(self, other):
    return isinstance(other, Location) and self.name == other.name


class Annotation(ABC):
  """Abstract base class for annotations with factory pattern support."""

  def __init__(self, value: float, label: str, color: str, type: str):
    """
    Initialize annotation with factory pattern support.
    """
    self.value = value
    self.label = label
    self.color = color
    self.type = type

  @classmethod
  def create(cls, value: float, label: str, color: str, type: str) -> 'Annotation':
    """Factory method to create appropriate annotation subclass based on type."""
    if not type:
      return HorizontalAnnotation(value, label, color)

    type_lower = type.lower()
    if type_lower == 'horizontal':
      return HorizontalAnnotation(value, label, color)
    elif type_lower == 'vertical':
      return VerticalAnnotation(value, label, color)
    else:
      raise ValueError(f'Invalid type "{type}". Must be "horizontal" or "vertical"')

  def to_dict(self) -> dict[str, Any]:
    """Convert object to dictionary for JSON serialization."""
    return asdict(self)

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> Self:
    """Create object from dictionary using factory pattern."""
    return cls.create(
      value=data['value'], label=data['label'], color=data['color'], type=data['type']
    )

  @staticmethod
  def get_cache_key(type: str, label: str, value: float) -> str:
    return f'annotation:{type}:{label}:{value}'

  def __hash__(self):
    return hash(self.value + self.label + self.type)

  def __eq__(self, other):
    return (
      isinstance(other, Annotation)
      and self.value == other.value
      and self.label == other.label
      and self.type == other.type
    )


class HorizontalAnnotation(Annotation):
  """Annotation that appears horizontally (on x-axis)."""

  def __init__(self, value: float, label: str, color: str):
    super().__init__(value, label, color, 'horizontal')


class VerticalAnnotation(Annotation):
  """Annotation that appears vertically (on y-axis)."""

  def __init__(self, value: float, label: str, color: str):
    super().__init__(value, label, color, 'vertical')


class PlotTitle:
  def __init__(
    self,
    pathogen: str,
    scenario: Scenario,
    models: list[Model],
    location: Location,
    age_group: AgeGroup,
  ):
    self.pathogen = pathogen
    self.scenario = scenario
    self.location = location
    self.age_group = age_group

  def __str__(self):
    return (
      f'{self.pathogen} Scenario {self.scenario}'
      + f'{(self.age_group.display_value + " ") if self.age_group else ""} in {self.location}'
    )

  def __hash__(self):
    return hash(
      self.pathogen + self.scenario.name + self.location.name + self.age_group.input_value
    )

  def __eq__(self, other):
    return (
      isinstance(other, PlotTitle)
      and self.pathogen == other.pathogen
      and self.scenario == other.scenario
      and self.location == other.location
      and self.age_group == other.age_group
    )


class PlotType(StrEnum):
  LINE = 'line'
  BOXPLOT = 'boxplot'

  def __hash__(self):
    return hash(self.value)

  def __eq__(self, other):
    return isinstance(other, PlotType) and self.value == other.value


class AxisRange:
  def __init__(self, min: str | None, max: str | None):
    self.min = min
    self.max = max


class Zoom:
  def __init__(self, x: dict[str, str] | None = None, y: dict[str, str] | None = None):
    if x is None:
      self.x = AxisRange(None, None)
    if y is None:
      self.y = AxisRange(None, None)
    else:
      self.x = AxisRange(x['min'], x['max'])
      self.y = AxisRange(y['min'], y['max'])


class ChartControls:
  def __init__(
    self,
    round_num: int,
    pathogen: str,
    scenario_names: list[str],
    model_names: list[str],
    location_name: str,
    target: str,
    age_group: str = '0-130',
    zoom: dict[str, dict[str, Any]] | None = None,
    annotations: list[dict[str, Any]] | None = None,
    certainty_percent: str | None = None,
  ):
    self.round_num = round_num
    self.pathogen = pathogen
    self.scenarios = [Scenario(name=scenario_name) for scenario_name in scenario_names]
    self.models = [Model(model_name) for model_name in model_names]
    self.location = Location(location_name)
    self.target = Target.from_input_value(target)
    self.age_group = AgeGroup.from_input_value(age_group)
    self.annotations = (
      [Annotation.from_dict(annotation) for annotation in annotations] if annotations else None
    )
    self.certainty_percent = (
      Uncertainty.from_display_value(certainty_percent) if certainty_percent else None
    )
    self.zoom = Zoom(zoom['x'], zoom['y']) if zoom else Zoom()


class Chart:
  """Chart class for displaying a chart"""

  def __init__(self, plot_type: PlotType, controls: ChartControls):
    self.plot_type = plot_type
    self.x_start_date = datetime.strptime('2025-01-01', '%Y-%m-%d')
    self.x_axis = 'target_end_date'
    self.y_axis = 'value'
    self.round_num = controls.round_num
    self.scenarios = controls.scenarios
    self.models = controls.models
    self.location = controls.location
    self.target = controls.target
    self.age_group = controls.age_group
    self.certainty_percent = controls.certainty_percent
    self.annotations = controls.annotations
    self.zoom = controls.zoom
    self._data_type = DataType.QUANTILE
    self._raw_df = Chart.collect_data(
      self._data_type, self.round_num, self.location.name, self.target.input_value
    )
    self._raw_df[self.x_axis] = pd.to_datetime(self._raw_df[self.x_axis])
    self._raw_df = self._raw_df.set_index(self.x_axis)
    self._fig = go.Figure()

    self.refresh_fig()

  def __hash__(self):
    return hash(
      self.plot_type
      + self.round_num
      + self.scenarios
      + self.models
      + self.location
      + self.target
      + self.age_group
      + self.certainty_percent
      + (self.annotations.__hash__() if self.annotations else '')
    )

  def __eq__(self, other):
    return (
      isinstance(other, Chart)
      and self.plot_type == other.plot_type
      and self.round_num == other.round_num
      and self.scenarios == other.scenarios
      and self.models == other.models
      and self.location == other.location
      and self.target == other.target
      and self.age_group == other.age_group
      and self.certainty_percent == other.certainty_percent
      and self.annotations == other.annotations
    )

  def _create_empty_figure(self):
    self._fig = go.Figure()
    # self._fig.update_xaxes(showspikes=True, spikemode='across', spikesnap='cursor')
    # self._fig.update_yaxes(showspikes=True, spikemode='across')

  def refresh_fig(self) -> go.Figure:
    # update layout
    num_rows = len(self.scenarios)
    self._fig.update_layout(
      hovermode='x unified', height=300 * num_rows, title='Forecast values over time (by scenario)'
    )

    # handle empty properties
    if not (self.scenarios and self.models and self.location and self.target):
      self._create_empty_figure()
      return self._fig
    if not self.scenarios:
      raise ValueError('Scenario is required to display chart.')
    if not self.models:
      raise ValueError('Models are required to display chart.')

    # start with the raw dataframe
    df = self._raw_df

    # filter data to start from x_start_date and use given age group
    # df = df.loc[[self.x_start_date :]]
    df = df.query('age_group == @self.age_group.input_value')

    # create boxplot if prudent
    if self.plot_type == PlotType.BOXPLOT:
      return px.box(df, y=self.y_axis)

    # otherwise,create subplots
    self._fig = make_subplots(
      rows=num_rows,
      cols=1,
      vertical_spacing=0.1,
      subplot_titles=[f'Scenario {s.name}' for s in self.scenarios],
    )

    # add traces for each scenario
    for i, scenario in enumerate(self.scenarios, start=1):
      scenario_df = df.query('scenario_id == @scenario.id')

      # set up uncertainty intervals if necessary
      should_add_uncertainty_intervals = (
        self.certainty_percent and self.certainty_percent in Uncertainty.display_values()
      )
      if should_add_uncertainty_intervals:
        uncertainty_bounds = Uncertainty.from_display_value(self.certainty_percent).get_bounds()
        for lower_q, upper_q in uncertainty_bounds:
          lower_data = scenario_df.query('type_id == @lower_q')
          upper_data = scenario_df.query('type_id == @upper_q')

      # add traces for each model
      main_data = scenario_df.query('type_id == 0.5')
      for model in self.models:
        # add uncertainty intervals if necessary
        if should_add_uncertainty_intervals and lower_data and upper_data and lower_q and upper_q:
          lower_model = lower_data.query('model_name == @model.id')
          upper_model = upper_data.query('model_name == @model.id')
          self._fig.add_trace(
            go.Scatter(
              x=pd.concat([lower_model.index, upper_model.index[::-1]]),
              y=pd.concat([lower_model[self.y_axis], upper_model[self.y_axis][::-1]]),
              fill='toself',
              fillcolor=conf_int_colors[(lower_q, upper_q)],
              line=dict(color='rgba(0,0,0,0)'),
              hoverinfo='skip',
              showlegend=False,
            ),
            row=i,
            col=1,
          )

        # add main line (0.5 quantile)
        model_df = main_data.query('model_name == @model.id')
        self._fig.add_trace(
          go.Scatter(
            x=model_df.index,
            y=model_df[self.y_axis],
            mode='lines',
            name=f'Model {model.name}',
            legendgroup=f'Model {model.name}',
            showlegend=(i == 1),
            line=dict(color=model.color),
          ),
          row=i,
          col=1,
        )

      # load gold standard data (the actual data up to present day, not projections)
      gold_std_df = Chart.collect_gold_std_data(self.round_num)
      gold_std_df['time_value'] = pd.to_datetime(gold_std_df['time_value'])
      gold_std_df = gold_std_df.set_index('time_value')
      gold_std_df = gold_std_df.query('age_group == @self.age_group.input_value')
      gold_std_df = gold_std_df.query('geo_value_fullname == @self.location.name')

      # filter gold standard data to start from x_start_date
      gold_std_df = gold_std_df.loc[self.x_start_date :]
      # gold_std_df = gold_std_df.query('time_value >= @self.x_start_date')

      # add gold standard line
      self._fig.add_trace(
        go.Scatter(
          x=gold_std_df.index,
          y=gold_std_df['value'],
          mode='lines',
          name='Gold standard',
          line=dict(color='black', dash='dot'),
          marker=dict(symbol='diamond'),
          legendgroup='Gold standard',
          showlegend=(i == 1),
        ),
        row=i,
        col=1,
      )

    # add annotations
    if self.annotations:
      for annotation in self.annotations:
        if annotation.type == 'horizontal':
          self._fig.add_hline(
            y=annotation.value,
            line_dash='dot',
            line_color=annotation.color,
            line_width=1,
            annotation_text=annotation.label,
          )
        else:
          self._fig.add_vline(
            x=annotation.value,
            line_dash='dot',
            line_color=annotation.color,
            line_width=1,
            annotation_text=annotation.label,
          )

    # updating axes
    self._fig.update_xaxes(matches='x', showspikes=True, spikemode='across', spikesnap='cursor')
    self._fig.update_yaxes(matches='y', showspikes=True, spikemode='across')

    # and zoom ranges
    if self.zoom.x.min is not None and self.zoom.x.max is not None:
      self._fig.update_xaxes(range=[self.zoom.x.min, self.zoom.x.max])
    if self.zoom.y.min is not None and self.zoom.y.max is not None:
      self._fig.update_yaxes(range=[self.zoom.y.min, self.zoom.y.max])

    self._fig.update_layout(
      hovermode='x unified',
      height=300 * num_rows,
      title='Forecast values over time (by scenario)',
      uirevision='df',
    )

    return self._fig

  def get_fig(self) -> go.Figure:
    return self._fig

  def get_data(self) -> pd.DataFrame:
    return self._raw_df

  @staticmethod
  @lru_cache(maxsize=128)
  def _build_dataset_path(
    data_type: DataType = DataType.QUANTILE,
    round_number: int = 1,
    location_name: str = 'US',
    target_value: str = 'incident_hospitalization',
    part: int = 0,
  ) -> Path:
    part = str(part)
    round_fragment = f'round{round_number}'
    path = (
      BASE_DATA_DIR
      / round_fragment
      / target_value
      / location_name
      / data_type.get_path_value()
      / f'part-{part}.{data_type.get_file_extension()}'
    )
    if not path.exists() or not path.is_file():
      raise FileNotFoundError(f'File not found for chart: {path}')
    return path

  @staticmethod
  @lru_cache(maxsize=64)
  def collect_data(
    data_type: DataType = DataType.QUANTILE,
    round_number: int = 1,
    location_name: str = 'US',
    target_value: str = 'incident_hospitalization',
    part: int = 0,
  ) -> pd.DataFrame:
    path = Chart._build_dataset_path(
      data_type=data_type,
      round_number=round_number,
      location_name=location_name,
      target_value=target_value,
      part=part,
    )
    if not path.exists() or not path.is_file():
      raise FileNotFoundError(f'File not found for chart: {path}')

    try:
      return pd.read_csv(path, parse_dates=['target_end_date'])
    except Exception as e:
      print(f'Error reading file "{path}": {e}')
      raise e

  @staticmethod
  @lru_cache(maxsize=32)
  def _build_gold_std_path(round_number: int) -> Path:
    return BASE_DATA_DIR / f'round{round_number}' / 'gold_standard' / 'covid_nhsn_hosp_inc.csv'

  @staticmethod
  @lru_cache(maxsize=32)
  def collect_gold_std_data(round_number: int) -> pd.DataFrame:
    gold_std_path = Chart._build_gold_std_path(round_number)
    if not gold_std_path.exists() or not gold_std_path.is_file():
      raise FileNotFoundError(f'File not found for gold standard data: {gold_std_path}')
    return pd.read_csv(gold_std_path, parse_dates=['time_value'])
