import copy
from abc import ABC, abstractmethod
from functools import lru_cache
from pathlib import Path
from typing import Any, Self

import pandas as pd
import plotly.graph_objects as go

from src.components.chart.chart_controls import DEFAULT_CONTROL_VALUES, ChartControls
from src.components.chart.chart_properties import (
  Annotation,
  DatetimeAxisRange,
  FloatAxisRange,
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
      DataType.QUANTILE,
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
        self.controls.saved_zoom.x.min
        if self.controls.saved_zoom and self.controls.saved_zoom.x.min
        else ''
      ),
      str(
        self.controls.saved_zoom.x.max
        if self.controls.saved_zoom and self.controls.saved_zoom.x.max
        else ''
      ),
      str(
        self.controls.saved_zoom.y.min
        if self.controls.saved_zoom and self.controls.saved_zoom.y.min
        else ''
      ),
      str(
        self.controls.saved_zoom.y.max
        if self.controls.saved_zoom and self.controls.saved_zoom.y.max
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

  def update_zoom(self, saved_zoom: Zoom | None, current_zoom: Zoom | None):
    """
    Update both saved_zoom and current_zoom.
    Note: current_zoom is calculated from relayoutData in callbacks, not stored in controls.
    """
    self.update_saved_zoom(saved_zoom)
    self.update_current_zoom(current_zoom)

  def update_current_zoom(self, current_zoom: Zoom | None):
    """
    Update current zoom and apply to all subplots with unified axes.
    This ensures that when one subplot is zoomed, all subplots are synchronized.
    """
    if current_zoom:
      # Update all x-axes and y-axes across all subplots
      self._fig.update_xaxes(range=[current_zoom.x.min, current_zoom.x.max])
      self._fig.update_yaxes(range=[current_zoom.y.min, current_zoom.y.max])

  def update_saved_zoom(self, saved_zoom: Zoom | None):
    """Update saved_zoom without refreshing the figure."""
    if saved_zoom:
      self.controls.saved_zoom = copy.deepcopy(saved_zoom)

  @staticmethod
  def calculate_zoom_from_relayout(relayout: dict[str, Any] | None) -> Zoom | None:
    """
    Calculate Zoom object from plotly relayoutData.
    Handles multiple subplots by extracting range from any subplot (they should be synchronized).
    Returns None if no valid zoom data is found.
    """
    if not relayout:
      return None
    x_range_min: str | float | None = None
    x_range_max: str | float | None = None
    y_range_min: str | float | None = None
    y_range_max: str | float | None = None

    for key in relayout.keys():
      if key.startswith('xaxis') and '.range' in key:
        if key.endswith('.range[0]'):
          x_range_min = relayout.get(key)
          range_key_1 = key.replace('.range[0]', '.range[1]')
          x_range_max = relayout.get(range_key_1)
        elif key.endswith('.range') and isinstance(relayout.get(key), list):
          x_range = relayout.get(key)
          if x_range and len(x_range) >= 2:
            x_range_min = x_range[0]
            x_range_max = x_range[1]
      elif key.startswith('yaxis') and '.range' in key:
        if key.endswith('.range[0]'):
          y_range_min = relayout.get(key)
          range_key_1 = key.replace('.range[0]', '.range[1]')
          y_range_max = relayout.get(range_key_1)
        elif key.endswith('.range') and isinstance(relayout.get(key), list):
          y_range = relayout.get(key)
          if y_range and len(y_range) >= 2:
            y_range_min = y_range[0]
            y_range_max = y_range[1]

    # Only create Zoom if we have all required values
    if (
      x_range_min is not None
      and x_range_max is not None
      and y_range_min is not None
      and y_range_max is not None
    ):
      try:
        return Zoom(x_min=x_range_min, x_max=x_range_max, y_min=y_range_min, y_max=y_range_max)
      except (ValueError, TypeError):
        return None
    return None

  def _get_axis_type(self, df: pd.DataFrame) -> type[DatetimeAxisRange] | type[FloatAxisRange]:
    if df.index.dtype == 'datetime64[ns]':
      return DatetimeAxisRange
    elif df.index.dtype == 'float64':
      return FloatAxisRange
    else:
      raise ValueError(f'Invalid index type: {df.index.dtype}')

  def _get_x_axis_range(self) -> DatetimeAxisRange | FloatAxisRange | None:
    """
    Get the x-axis range as a DatetimeAxisRange or FloatAxisRange object.
    Returns None if the range cannot be determined.
    """
    # Try saved_zoom first
    if self.controls.saved_zoom:
      return self.controls.saved_zoom.x

    # Try to get range from figure layout
    xaxis = self._fig.layout.xaxis
    if hasattr(xaxis, 'range') and xaxis.range:
      x_min_val = xaxis.range[0]
      x_max_val = xaxis.range[1]
      axis_type = self._get_axis_type(self._raw_df)
      return axis_type(min=x_min_val, max=x_max_val)
    return None

  def _get_x_axis_midpoint(self) -> float | None:
    """
    Calculate the midpoint of the x-axis range in milliseconds.
    Returns None if the range cannot be determined.
    """
    x_range = self._get_x_axis_range()
    if x_range is not None:
      if isinstance(x_range, DatetimeAxisRange):
        return DatetimeAxisRange.datetime_to_milliseconds(x_range.midpoint())
      elif isinstance(x_range, FloatAxisRange):
        return x_range.midpoint()
    return None

  def _get_y_float_axis_range(self) -> FloatAxisRange | None:
    """
    Get the y-axis range as a FloatAxisRange object.
    Returns None if the range cannot be determined.
    """
    yaxis: dict = self._fig.layout.yaxis.range
    y_min_val = yaxis['range'][0]
    y_max_val = yaxis['range'][1]
    return FloatAxisRange(min=y_min_val, max=y_max_val)

  def _get_y_axis_midpoint(self) -> float | None:
    """
    Calculate the midpoint of the y-axis range.
    Returns None if the range cannot be determined.
    """
    y_range = self._get_y_float_axis_range()
    if y_range is not None:
      return y_range.midpoint()
    return None

  def _plot_annotations(self):
    if not self.controls.annotations:
      return

    for annotation in self.controls.annotations:
      if isinstance(annotation, HorizontalAnnotation):
        y_value = annotation.value or 0

        # Determine annotation position based on whether it's on top or bottom half of y-axis
        y_midpoint = self._get_y_axis_midpoint()
        if y_midpoint is not None:
          if y_value > y_midpoint:
            annotation_position = 'bottom left'
          else:
            annotation_position = 'top left'
        else:
          annotation_position = 'bottom left'

        self._fig.add_hline(
          y=y_value,
          line_dash='dot',
          line_color=annotation.color,
          line_width=1,
          annotation_text=annotation.label,
          annotation_position=annotation_position,
        )
      elif isinstance(annotation, VerticalAnnotation):
        ms = (
          DatetimeAxisRange.datetime_to_milliseconds(
            DatetimeAxisRange.parse_value(annotation.value)
          )
          if annotation.value
          else None
        )

        # Determine annotation position based on whether it's on left or right half of x-axis
        x_midpoint_ms = self._get_x_axis_midpoint()
        if x_midpoint_ms is not None and ms is not None:
          if ms < x_midpoint_ms:
            annotation_position = 'top right'
          else:
            annotation_position = 'top left'
        else:
          annotation_position = 'top left'

        self._fig.add_vline(
          x=ms,
          line_dash='dot',
          line_color=annotation.color,
          line_width=1,
          annotation_text=annotation.label,
          annotation_position=annotation_position,
        )
      else:
        raise ValueError(f'Invalid annotation type: {annotation.type}')

  @staticmethod
  @lru_cache(maxsize=128)
  def _build_dataset_path(
    data_type: DataType = DataType.QUANTILE,
    round_number: int = DEFAULT_CONTROL_VALUES.get('round_num'),
    location_name: str = DEFAULT_CONTROL_VALUES.get('location_name'),
    target_value: str = DEFAULT_CONTROL_VALUES.get('target'),
    part: int = 0,
  ) -> Path:
    path = (
      BASE_DATA_DIR
      / f'round{round_number}'
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
