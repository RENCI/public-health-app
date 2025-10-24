from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Any, Self

import pandas as pd
import plotly.graph_objects as go
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
    key_components = [str(self.type), str(self.label), str(self.value)]
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
    plot_type: str,
    round_num: int,
    scenario_names: list[str],
    model_names: list[str],
    location_name: str,
    target: str,
    age_group: str,
    x_axis: str,
    y_axis: str,
    x_start_date: str | None = None,
    zoom: dict[str, dict[str, Any]] | None = None,
    annotations: list[dict[str, Any]] | None = None,
    certainty_percent: str | None = None,
    pathogen: str = 'covid',
  ):
    self.plot_type = PlotType(plot_type)
    self.round_num = round_num
    self.pathogen = pathogen
    self.scenarios = [Scenario(name=scenario_name) for scenario_name in scenario_names]
    self.models = [Model(model_name) for model_name in model_names]
    self.location = Location(location_name)
    self.target = Target.from_input_value(target)
    self.age_group = AgeGroup.from_input_value(age_group)
    self.x_axis = x_axis
    self.y_axis = y_axis
    self.x_start_date = datetime.strptime(x_start_date, '%Y-%m-%d') if x_start_date else None
    self.annotations = (
      [Annotation.from_dict(annotation) for annotation in annotations] if annotations else None
    )
    self.certainty_percent = (
      CertaintyInterval.from_display_value(certainty_percent) if certainty_percent else None
    )
    self.zoom = Zoom(zoom['x'], zoom['y']) if zoom else Zoom()
    self.data_type = DataType.QUANTILE


class Chart(ABC):
  """Abstract base class for charts. Contains common properties and methods for all charts."""

  def __init__(self, controls: ChartControls):
    """
    Initialize the base chart class. This gets called first by the concrete chart classes'
    constructors.
    """
    self.controls = controls

    self._raw_df: pd.DataFrame = pd.DataFrame()
    self._fig: go.Figure = self._create_empty_figure()

  @staticmethod
  def create(controls: ChartControls) -> 'Chart':
    plot_type = controls.plot_type
    if plot_type == PlotType.LINE:
      return LineChart(controls)
    elif plot_type == PlotType.BOXPLOT:
      return BoxplotChart(controls)
    else:
      raise ValueError(f'Invalid plot type: {plot_type}')

  def _create_empty_figure(self) -> go.Figure:
    return go.Figure()

  @abstractmethod
  def refresh_fig(self) -> go.Figure:
    pass

  @abstractmethod
  def _reload_data(self):
    pass

  @staticmethod
  def get_key(controls: ChartControls) -> str:
    """
    Generate a unique string key from chart controls.
    This creates a deterministic string representation that can be used as a dictionary key.
    """
    # Create a deterministic string representation of the chart parameters
    key_components = [
      str(controls.plot_type),
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

  @abstractmethod
  def __hash__(self) -> int:
    pass

  @abstractmethod
  def __eq__(self, other: Self) -> bool:
    pass

  def get_fig(self) -> go.Figure:
    return self._fig

  def get_raw_dataframe(self) -> pd.DataFrame:
    return self._raw_df

  def update_controls(self, controls: ChartControls):
    """
    Update the chart controls and refresh the figure without recreating the entire chart object.
    This method updates the chart parameters and regenerates the figure with new data.
    """
    # Only update if the controls have changed
    if controls != self.controls:
      self.controls = controls
      self._reload_data()
      self.refresh_fig()

  def update_round_num(self, round_num: int):
    self.controls.round_num = round_num
    self._reload_data()
    self.refresh_fig()

  def update_pathogen(self, pathogen: str):
    self.controls.pathogen = pathogen
    self._reload_data()
    self.refresh_fig()

  def update_scenarios(self, scenario_names: list[str]):
    self.controls.scenarios = [Scenario(name=scenario_name) for scenario_name in scenario_names]
    self.refresh_fig()

  def update_models(self, model_names: list[str]):
    self.controls.models = [Model(model_name) for model_name in model_names]
    self.refresh_fig()

  def update_location(self, location_name: str):
    self.controls.location = Location(location_name)
    self._reload_data()
    self.refresh_fig()

  def update_target(self, target: str):
    self.controls.target = Target.from_input_value(target)
    self._reload_data()
    self.refresh_fig()

  def update_age_group(self, age_group: str):
    self.controls.age_group = AgeGroup.from_input_value(age_group)
    self._reload_data()
    self.refresh_fig()

  def update_annotations(self, annotations: list[dict[str, Any]] | None):
    self.controls.annotations = (
      [Annotation.from_dict(annotation) for annotation in annotations] if annotations else None
    )
    # might be able to get away with just calling _plot_annotations() here instead of refresh_fig()
    # since annotations are not data-dependent
    self.refresh_fig()

  def update_zoom(self, zoom: dict[str, dict[str, Any]] | None):
    self.controls.zoom = Zoom(zoom['x'], zoom['y']) if zoom else Zoom()
    self.refresh_fig()

  def _plot_annotations(self):
    if not self.controls.annotations:
      return
    # Clear existing annotations. We will rebuild them below.
    self._fig.layout.shapes = []
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
    data_type: DataType,
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


class LineChart(Chart):
  """Chart class for displaying a chart"""

  def __init__(self, controls: ChartControls):
    super().__init__(controls)
    self._raw_df = Chart.collect_data(
      self.controls.data_type,
      self.controls.round_num,
      self.controls.location.name,
      self.controls.target.input_value,
    )
    self._raw_df[self.controls.x_axis] = pd.to_datetime(self._raw_df[self.controls.x_axis])
    self._raw_df = self._raw_df.set_index(self.controls.x_axis)
    self._fig = go.Figure()

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
            y=primary_line_data[self.controls.y_axis],
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
      gold_std_df = gold_std_df.loc[self.controls.x_start_date or gold_std_df.index.min() :]

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
    self._fig.update_yaxes(title_text=self.controls.target.display_value)

    self._fig.update_layout(
      hovermode='x unified',
      height=chart_total_height + 180,
      title=self.get_title(),
      title_subtitle_text=self.get_subtitle(),
      uirevision=self.__hash__(),
    )

    return self._fig

  def get_fig(self) -> go.Figure:
    return self._fig

  def get_raw_dataframe(self) -> pd.DataFrame:
    return self._raw_df

  def get_title(self) -> str:
    return f'{self.controls.target.display_value} over time (by scenario)'

  def get_subtitle(self) -> str:
    return f'Pathogen: {self.controls.pathogen} | Location: {self.controls.location.name} | Age group: {self.controls.age_group.display_value}'

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

  def update_certainty_percent(self, certainty_percent: str | None):
    """
    Update the certainty percentage.
    """
    self.controls.certainty_percent = (
      CertaintyInterval.from_display_value(certainty_percent) if certainty_percent else None
    )
    self.refresh_fig()

  def _plot_certainty_interval(self, scenario_df: pd.DataFrame, model: Model, row_num: int):
    for lower_q, upper_q in self.controls.certainty_percent.get_bounds():
      lower_model = scenario_df.query('type_id == @lower_q and model_name == @model.id')
      upper_model = scenario_df.query('type_id == @upper_q and model_name == @model.id')
      self._fig.add_trace(
        go.Scatter(
          x=pd.concat([lower_model.index.to_series(), upper_model.index.to_series()[::-1]]),
          y=pd.concat([lower_model[self.controls.y_axis], upper_model[self.controls.y_axis][::-1]]),
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
          y=scenario_df[self.controls.y_axis],
          marker_color=get_model_color_by_id(ensemble_model_id),
        ),
        row=i,
        col=1,
        secondary_y=False,
      )
      self._fig.add_trace(
        go.Box(
          y=scenario_df[self.controls.y_axis],
          marker_color=get_model_color_by_id(ensemble_model_id),
        ),
        row=i,
        col=2,
        secondary_y=True,
      )

    # plot annotations
    self._plot_annotations()

    # update axes
    self._fig.update_xaxes(showspikes=True, spikemode='across', spikesnap='cursor')
    for row in range(1, num_rows + 1):
      y_axis_num = f'y{row}'
      for col in range(1, num_cols + 1):
        # Only set y-axis title for second column (secondary_y=True)
        y_axis_title = f'Scenario {self.controls.scenarios[row - 1].name}' if col == 2 else None
        self._fig.update_yaxes(
          showspikes=True,
          spikemode='across',
          matches=y_axis_num,
          row=row,
          col=col,
          title_text=y_axis_title,
          secondary_y=(col == 2),
        )

    # update zoom ranges
    if self.controls.zoom.x.min and self.controls.zoom.x.max:
      self._fig.update_xaxes(range=[self.controls.zoom.x.min, self.controls.zoom.x.max])
    if self.controls.zoom.y.min and self.controls.zoom.y.max:
      self._fig.update_yaxes(range=[self.controls.zoom.y.min, self.controls.zoom.y.max])

    self._fig.update_layout(
      hovermode='closest',
      height=400 + (200 * max(0, num_rows - 1)),
      title='Forecast distribution (boxplot)',
      uirevision=self.__hash__(),
    )

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
