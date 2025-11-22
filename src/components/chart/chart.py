from abc import ABC, abstractmethod
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Self

import pandas as pd
import plotly.graph_objects as go

from src.components.chart.chart_controls import ChartControls
from src.components.chart.chart_properties import (
  Annotation,
  HorizontalAnnotation,
  Location,
  Model,
  Scenario,
  VerticalAnnotation,
  Zoom,
)
from src.components.enums import AgeGroup, DataType, Target

BASE_DATA_DIR = Path(__file__).resolve().parent.parent.parent / 'data' / 'rounds'


class Chart(ABC):
  """Abstract base class for charts. Contains common properties and methods for all charts."""

  def __init__(self, controls: ChartControls):
    """
    Initialize the base chart class. This gets called first by the concrete chart classes'
    constructors.
    """
    self.controls = controls
    self.load_data()
    self._fig: go.Figure = self._create_empty_figure()
    self.set_theme()

  def _create_empty_figure(self) -> go.Figure:
    return go.Figure()

  def set_theme(self):
    if self.controls.theme and self.controls.theme == 'light':
      self.set_theme_light()
    elif self.controls.theme and self.controls.theme == 'dark':
      self.set_theme_dark()
    else:
      self.set_theme_light()

  def set_theme_light(self):
    self._fig.update_layout(template='plotly_white')

  def set_theme_dark(self):
    self._fig.update_layout(template='plotly_dark')

  @abstractmethod
  def refresh_fig(self) -> go.Figure:
    pass

  def load_data(self):
    self._raw_df = Chart.collect_data(
      self.controls.data_type,
      self.controls.round_num,
      self.controls.location.name,
      self.controls.target.input_value,
    )
    self._gold_std_df = Chart.collect_gold_std_data(self.controls.round_num)
    self._gold_std_df = self._gold_std_df.query('age_group == @self.controls.age_group.input_value')
    self._gold_std_df = self._gold_std_df.query(
      'geo_value_fullname == @self.controls.location.name'
    )
    self._gold_std_df = self._gold_std_df.set_index('time_value')
    self._gold_std_df = self._gold_std_df[self._gold_std_df.index >= pd.to_datetime('2024-09-01')]

  @abstractmethod
  def get_title(self) -> str:
    pass

  @abstractmethod
  def get_subtitle(self) -> str:
    pass

  def get_key(self) -> str:
    """
    Generate a unique string key from chart controls.
    This creates a deterministic string representation that can be used as a dictionary key.
    """
    # Create a deterministic string representation of the chart parameters
    key_components = [
      str(self.controls.plot_type),
      str(self.controls.round_num),
      str(sorted([s.name for s in self.controls.scenarios])),
      str(sorted([m.name for m in self.controls.models])),
      str(self.controls.location.name),
      str(self.controls.target.input_value),
      str(self.controls.age_group.input_value),
      str(
        self.controls.uncertainty_interval.display_value
        if self.controls.uncertainty_interval
        else ''
      ),
      str(
        self.controls.zoom.x.get('min')
        if self.controls.zoom and self.controls.zoom.x.get('min')
        else ''
      ),
      str(
        self.controls.zoom.x.get('max')
        if self.controls.zoom and self.controls.zoom.x.get('max')
        else ''
      ),
      str(
        self.controls.zoom.y.get('min')
        if self.controls.zoom and self.controls.zoom.y.get('min')
        else ''
      ),
      str(
        self.controls.zoom.y.get('max')
        if self.controls.zoom and self.controls.zoom.y.get('max')
        else ''
      ),
      str(
        sorted([a.get_key() for a in self.controls.annotations])
        if self.controls.annotations
        else []
      ),
    ]
    # Use a deterministic string key
    return '|'.join(key_components)

  @abstractmethod
  def __hash__(self) -> int:
    """
    Generate a unique hash for chart instances based on their parameters.
    This creates a deterministic string representation that can be used as a key.
    """
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
      self.load_data()
      self.refresh_fig()

  def update_round_num(self, round_num: int):
    self.controls.round_num = round_num
    self.load_data()
    self.refresh_fig()

  def update_pathogen(self, pathogen: str):
    self.controls.pathogen = pathogen
    self.load_data()
    self.refresh_fig()

  def update_scenarios(self, scenario_names: list[str]):
    self.controls.scenarios = [Scenario(name=scenario_name) for scenario_name in scenario_names]
    self.refresh_fig()

  def update_models(self, model_names: list[str]):
    self.controls.models = [Model(model_name) for model_name in model_names]
    self.refresh_fig()

  def update_location(self, location_name: str):
    self.controls.location = Location(location_name)
    self.load_data()
    self.refresh_fig()

  def update_target(self, target: str):
    self.controls.target = Target.from_input_value(target)
    self.load_data()
    self.refresh_fig()

  def update_age_group(self, age_group: str):
    self.controls.age_group = AgeGroup.from_input_value(age_group)
    self.load_data()
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
