from abc import ABC
from dataclasses import asdict
from datetime import datetime
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Any, Self

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc
from plotly.subplots import make_subplots

from src.components.enums import AgeGroup, CertaintyInterval, DataType, Target
from src.constants import (
  get_locations,
  get_model_color_by_id,
  get_model_id,
  get_model_name,
  get_scenario_id,
  get_scenario_name,
)

BASE_DATA_DIR = Path(__file__).resolve().parent.parent / 'data' / 'rounds'
# mapping confidence interval value to quantile bounds
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
    self.color = get_model_color_by_id(self.id)

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

  def __init__(self, value: Any, label: str, color: str, type: str):
    """
    Initialize annotation with factory pattern support.
    """
    self.value = value
    self.label = label
    self.color = color
    self.type = type

  @classmethod
  def create(cls, value: Any, label: str, color: str, type: str) -> 'Annotation':
    """Factory method to create appropriate annotation subclass based on type."""
    if not type:
      if isinstance(value, str):
        value = datetime.strptime(value, '%Y-%m-%d')
        return VerticalAnnotation(value, label, color)
      elif isinstance(value, float):
        return HorizontalAnnotation(value, label, color)
      else:
        raise ValueError(f'Invalid value type "{type(value)}".')

    type_lower = type.lower()
    if type_lower == 'horizontal':
      return HorizontalAnnotation(value, label, color)
    elif type_lower == 'vertical':
      return VerticalAnnotation(value, label, color)
    else:
      raise ValueError(f'Invalid type "{type}".')

  def to_dict(self) -> dict[str, Any]:
    """Convert object to dictionary for JSON serialization."""
    return asdict(self)

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> Self:
    """Create object from dictionary using factory pattern."""
    if not data['type']:
      return HorizontalAnnotation(data['value'], data['label'], data['color'])
    return cls.create(
      value=data['value'], label=data['label'], color=data['color'], type=data['type']
    )

  @staticmethod
  def get_cache_key(type: str, label: str, value: float | datetime) -> str:
    return f'annotation:{type}:{label}:{value}'

  # Create a deterministic string representation of the chart parameters
  def get_key(self) -> str:
    key_components = [
      str(self.type),
      str(self.label),
      str(self.value),
    ]
    return '|'.join(key_components)

  def __hash__(self):
    return hash(self.get_key())

  def __eq__(self, other):
    return (
      isinstance(other, Annotation)
      and self.value == other.value
      and self.label == other.label
      and self.type == other.type
    )

  def __str__(self):
    return f'{self.label}: {self.value}, {self.type}'


class HorizontalAnnotation(Annotation):
  """Annotation that appears horizontally (on x-axis)."""

  def __init__(self, value: float, label: str, color: str):
    super().__init__(value, label, color, 'horizontal')


class VerticalAnnotation(Annotation):
  """Annotation that appears vertically (on y-axis)."""

  def __init__(self, value: datetime, label: str, color: str):
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
    plot_type: str = 'line',
    round_num: int = 19,
    pathogen: str = 'covid',
    scenario_names: list[str] = ['A-2023-10-27', 'B-2023-10-27'],
    model_names: list[str] = ['Ensemble'],
    location_name: str = 'US',
    target: str = 'incident_hospitalization',
    age_group: str = '0-130',
    x_start_date: str = '2025-01-01',
    x_axis: str = 'target_end_date',
    y_axis: str = 'value',
    zoom: dict[str, dict[str, Any]] | None = None,
    annotations: list[dict[str, Any]] | None = None,
    certainty_percent: str | None = None,
  ):
    self.plot_type = PlotType(plot_type)
    self.round_num = round_num
    self.pathogen = pathogen
    self.scenarios = [Scenario(name=scenario_name) for scenario_name in scenario_names]
    self.models = [Model(model_name) for model_name in model_names]
    self.location = Location(location_name)
    self.target = Target.from_input_value(target)
    self.age_group = AgeGroup.from_input_value(age_group)
    self.x_start_date = datetime.strptime(x_start_date, '%Y-%m-%d')
    self.x_axis = x_axis
    self.y_axis = y_axis
    self.annotations = (
      [Annotation.from_dict(annotation) for annotation in annotations] if annotations else None
    )
    self.certainty_percent = (
      CertaintyInterval.from_display_value(certainty_percent) if certainty_percent else None
    )
    self.zoom = Zoom(zoom['x'], zoom['y']) if zoom else Zoom()


class Chart:
  """Chart class for displaying a chart"""

  def __init__(self, plot_type: PlotType, controls: ChartControls):
    self.plot_type = plot_type
    self.controls = controls
    self.x_start_date = self.controls.x_start_date
    self.x_axis = self.controls.x_axis
    self.y_axis = self.controls.y_axis
    self._data_type = DataType.QUANTILE
    self._raw_df = Chart.collect_data(
      self._data_type,
      self.controls.round_num,
      self.controls.location.name,
      self.controls.target.input_value,
    )
    self._raw_df[self.x_axis] = pd.to_datetime(self._raw_df[self.x_axis])
    self._raw_df = self._raw_df.set_index(self.x_axis)
    self._fig = go.Figure()

    self.refresh_fig()

  @staticmethod
  def get_key(plot_type: PlotType, controls: ChartControls) -> str:
    """
    Generate a unique string key from chart controls and plot type.
    This creates a deterministic string representation that can be used as a dictionary key.
    """
    # Create a deterministic string representation of the chart parameters
    key_components = [
      str(plot_type),
      str(controls.round_num),
      str(sorted([s.name for s in controls.scenarios])),
      str(sorted([m.name for m in controls.models])),
      str(controls.location.name),
      str(controls.target.input_value),
      str(controls.age_group.input_value),
      str(controls.certainty_percent.display_value if controls.certainty_percent else ''),
      str(controls.zoom.x.min if controls.zoom.x.min else ''),
      str(controls.zoom.x.max if controls.zoom.x.max else ''),
      str(controls.zoom.y.min if controls.zoom.y.min else ''),
      str(controls.zoom.y.max if controls.zoom.y.max else ''),
      str(sorted([a.get_key() for a in controls.annotations]) if controls.annotations else []),
    ]
    # Use a deterministic string key
    return '|'.join(key_components)

  def __hash__(self):
    """
    Generate a unique hash for chart instances based on their parameters.
    This creates a deterministic string representation that can be used as a key.
    """
    return hash(self.get_key(self.plot_type, self.controls))

  def __eq__(self, other):
    return (
      isinstance(other, Chart)
      and self.plot_type == other.plot_type
      and self.controls == other.controls
    )

  def _create_empty_figure(self):
    self._fig = go.Figure()
    # self._fig.update_xaxes(showspikes=True, spikemode='across', spikesnap='cursor')
    # self._fig.update_yaxes(showspikes=True, spikemode='across')

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
    if not self.controls.scenarios:
      raise ValueError('Scenario is required to display chart.')
    if not self.controls.models:
      raise ValueError('Models are required to display chart.')

    # update layout
    num_rows = len(self.controls.scenarios)
    # Define fixed dimensions
    SUBPLOT_HEIGHT = 300  # Fixed height per subplot in pixels
    FIXED_SPACING = 50  # Fixed spacing between subplots in pixels

    # Calculate total figure height accounting for fixed spacing
    chart_total_height = (SUBPLOT_HEIGHT * num_rows) + (FIXED_SPACING * (num_rows - 1))

    # Calculate vertical_spacing as a fraction of total height
    # This ensures the actual pixel spacing remains constant
    if num_rows > 1:
      vertical_spacing = FIXED_SPACING / chart_total_height
    else:
      vertical_spacing = 0  # No spacing needed for single subplot

    # start with the raw dataframe
    df = self._raw_df

    # use given age group
    df = df.query('age_group == @self.controls.age_group.input_value')

    # create boxplot if prudent
    if self.plot_type == PlotType.BOXPLOT:
      return px.box(df, y=self.y_axis)

    # otherwise,create subplots
    self._fig = make_subplots(
      rows=num_rows,
      cols=1,
      vertical_spacing=vertical_spacing,
      row_heights=[1] * num_rows,
      subplot_titles=[f'Scenario {s.name}' for s in self.controls.scenarios],
    )

    # add traces for each scenario
    for i, scenario in enumerate(self.controls.scenarios, start=1):
      scenario_df = df.query('scenario_id == @scenario.id')

      # decide whether to add certainty intervals
      should_add_certainty_intervals = (
        self.controls.certainty_percent
        and self.controls.certainty_percent.display_value in CertaintyInterval.display_values()
      )

      # add traces for each model
      for model in self.controls.models:
        # add certainty intervals if necessary
        if should_add_certainty_intervals:
          self._plot_certainty_interval(scenario_df=scenario_df, model=model, row_num=i)

        # add main line (0.5 quantile)
        primary_line_data = scenario_df.query('type_id == 0.5 and model_name == @model.id')
        self._fig.add_trace(
          go.Scatter(
            x=primary_line_data.index,
            y=primary_line_data[self.y_axis],
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
      gold_std_df = Chart.collect_gold_std_data(self.controls.round_num)
      gold_std_df['time_value'] = pd.to_datetime(gold_std_df['time_value'])
      gold_std_df = gold_std_df.set_index('time_value')
      gold_std_df = gold_std_df.query('age_group == @self.controls.age_group.input_value')
      gold_std_df = gold_std_df.query('geo_value_fullname == @self.controls.location.name')

      # filter gold standard data to start from x_start_date
      gold_std_df = gold_std_df.loc[self.x_start_date :]

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

    # plot annotations
    self._plot_annotations()

    # update axes
    self._fig.update_xaxes(matches='x', showspikes=True, spikemode='across', spikesnap='cursor')
    self._fig.update_yaxes(matches='y', showspikes=True, spikemode='across')

    # update zoom ranges
    if self.controls.zoom.x.min is not None and self.controls.zoom.x.max is not None:
      self._fig.update_xaxes(range=[self.controls.zoom.x.min, self.controls.zoom.x.max])
    if self.controls.zoom.y.min is not None and self.controls.zoom.y.max is not None:
      self._fig.update_yaxes(range=[self.controls.zoom.y.min, self.controls.zoom.y.max])

    self._fig.update_layout(
      hovermode='x unified',
      height=chart_total_height + 180,
      title='Forecast values over time (by scenario)',
      uirevision=self.__hash__(),
    )

    return self._fig

  def get_fig(self) -> go.Figure:
    return self._fig

  def get_graph(self) -> dcc.Graph:
    return dcc.Graph(id='graph', figure=self._fig)

  def get_raw_dataframe(self) -> pd.DataFrame:
    return self._raw_df

  def update_controls(self, controls: ChartControls) -> None:
    """
    Update the chart controls and refresh the figure without recreating the entire chart object.
    This method updates the chart parameters and regenerates the figure with new data.
    """
    # Update the controls object
    self.controls = controls

    # Reload data if location or target changed
    self._reload_data()

    # Refresh the figure with new data and parameters
    self.refresh_fig()

  def _reload_data(self) -> None:
    """
    Reload data if location or target changed.
    This is called by individual update methods when data-dependent fields change.
    """
    new_raw_df = Chart.collect_data(
      self._data_type,
      self.controls.round_num,
      self.controls.location.name,
      self.controls.target.input_value,
    )
    new_raw_df[self.x_axis] = pd.to_datetime(new_raw_df[self.x_axis])
    new_raw_df = new_raw_df.set_index(self.x_axis)
    self._raw_df = new_raw_df

  def update_round_num(self, round_num: int) -> None:
    """
    Update the round number and reload data.
    """
    self.controls.round_num = round_num
    self._reload_data()
    self.refresh_fig()

  def update_pathogen(self, pathogen: str) -> None:
    """
    Update the pathogen name.
    """
    self.controls.pathogen = pathogen
    self.refresh_fig()

  def update_scenarios(self, scenario_names: list[str]) -> None:
    """
    Update the scenarios list.
    """
    self.controls.scenarios = [Scenario(name=scenario_name) for scenario_name in scenario_names]
    self.refresh_fig()

  def update_models(self, model_names: list[str]) -> None:
    """
    Update the models list.
    """
    self.controls.models = [Model(model_name) for model_name in model_names]
    self.refresh_fig()

  def update_location(self, location_name: str) -> None:
    """
    Update the location and reload data.
    """
    self.controls.location = Location(location_name)
    self._reload_data()
    self.refresh_fig()

  def update_target(self, target: str) -> None:
    """
    Update the target and reload data.
    """
    self.controls.target = Target.from_input_value(target)
    self._reload_data()
    self.refresh_fig()

  def update_age_group(self, age_group: str) -> None:
    """
    Update the age group.
    """
    self.controls.age_group = AgeGroup.from_input_value(age_group)
    self.refresh_fig()

  def update_annotations(self, annotations: list[dict[str, Any]] | None) -> None:
    """
    Update the annotations list.
    """
    self.controls.annotations = (
      [Annotation.from_dict(annotation) for annotation in annotations] if annotations else None
    )
    self.refresh_fig()

  def update_certainty_percent(self, certainty_percent: str | None) -> None:
    """
    Update the certainty percentage.
    """
    self.controls.certainty_percent = (
      CertaintyInterval.from_display_value(certainty_percent) if certainty_percent else None
    )
    self.refresh_fig()

  def update_zoom(self, zoom: dict[str, dict[str, Any]] | None) -> None:
    """
    Update the zoom settings.
    """
    self.controls.zoom = Zoom(zoom['x'], zoom['y']) if zoom else Zoom()
    self.refresh_fig()

  def _plot_certainty_interval(
    self, scenario_df: pd.DataFrame, model: Model, row_num: int
  ) -> go.Figure:
    for lower_q, upper_q in self.controls.certainty_percent.get_bounds():
      lower_model = scenario_df.query('type_id == @lower_q and model_name == @model.id')
      upper_model = scenario_df.query('type_id == @upper_q and model_name == @model.id')
      self._fig.add_trace(
        go.Scatter(
          x=pd.concat([lower_model.index.to_series(), upper_model.index.to_series()[::-1]]),
          y=pd.concat([lower_model[self.y_axis], upper_model[self.y_axis][::-1]]),
          fill='toself',
          fillcolor=conf_int_colors[(lower_q, upper_q)],
          line=dict(color='rgba(0,0,0,0)'),
          legendgroup=f'Model {model.name}',
          hoverinfo='skip',
          showlegend=False,
        ),
        row=row_num,
        col=1,
      )

  def _plot_annotations(self) -> go.Figure:
    if not self.controls.annotations:
      return
    for annotation in self.controls.annotations:
      if isinstance(annotation, HorizontalAnnotation):
        self._fig.add_hline(
          y=annotation.value or 0,
          line_dash='dot',
          line_color=annotation.color,
          line_width=1,
          annotation_text=annotation.label,
        )
      elif isinstance(annotation, VerticalAnnotation):
        # Convert date to timestamp in milliseconds, as there passing the datetime object directly and adding annotation_text causes a TypeError
        # See: https://github.com/plotly/plotly.py/issues/3065
        # Assuming date is in "YYYY-MM-DD" format
        ms = (
          datetime.strptime(annotation.value, '%Y-%m-%d').timestamp() * 1000
          if annotation.value
          else None
        )

        self._fig.add_vline(
          x=ms,
          line_dash='dot',
          line_color=annotation.color,
          line_width=1,
          annotation_text=annotation.label,
        )
      else:
        raise ValueError(f'Invalid annotation type: {annotation.type}')
    return self._fig

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
