from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Self

from src.util.constants import (
  get_locations,
  get_model_by_name,
  get_scenario_by_id,
)


@dataclass
class Scenario:
  id: int
  name: str
  description: str
  round: int

  def __init__(self, id: int):
    scenario_data = get_scenario_by_id(id)
    self.id = scenario_data['id']
    self.name = scenario_data['name']
    self.description = scenario_data['description']
    self.round = scenario_data['round']


@dataclass
class ScenarioVariable:
  name: str
  options: list[str]
  selected_option: str


@dataclass
class Model:
  id: int
  name: str
  color: str

  def __init__(self, model_name: str):
    self.name = model_name
    model_data = get_model_by_name(model_name)
    self.id = model_data['id']
    self.color = model_data['color']


@dataclass
class Location:
  name: str
  short_code: str
  index: int
  population: int

  # Override __init__ to correctly initialize the location name and data, and
  # to handle the special case of 'US'
  def __init__(self, location_name: str):
    if location_name.upper() == 'US':
      self.name = location_name.upper()
    else:
      self.name = location_name.lower().capitalize()
    location_data = get_locations()[self.name]
    self.short_code, self.index, self.population = location_data


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


@dataclass
class DatetimeAxisRange:
  min: datetime
  max: datetime

  def __init__(self, min: str | datetime | None, max: str | datetime | None):
    def parse_value(value: str | datetime | None) -> datetime:
      if value is None:
        raise ValueError('Value for DatetimeAxisRange cannot be None.')
      if isinstance(value, datetime):
        return value
      if not isinstance(value, str) or value == '':
        raise ValueError(f'Value "{value}" for DatetimeAxisRange cannot be empty.')

      # First try ISO format parsing (handles formats like "2024-11-02T00:00:00")
      # This handles various ISO 8601 formats including with/without microseconds and timezone
      try:
        # Handle 'Z' timezone indicator by replacing with +00:00
        iso_value = value.replace('Z', '+00:00') if value.endswith('Z') else value
        return datetime.fromisoformat(iso_value)
      except (ValueError, AttributeError):
        pass

      # Try multiple datetime formats
      datetime_formats = [
        '%Y-%m-%dT%H:%M:%S.%f',  # 2024-11-02T00:00:00.000000
        '%Y-%m-%dT%H:%M:%S',  # 2024-11-02T00:00:00
        '%Y-%m-%dT%H:%M',  # 2024-11-02T00:00
        '%Y-%m-%d %H:%M:%S.%f',  # 2025-09-30 12:00:34.1455
        '%Y-%m-%d %H:%M:%S',  # 2025-09-30 12:00:34
        '%Y-%m-%d %H:%M',  # 2025-09-30 12:00
        '%Y-%m-%d',  # 2025-09-30
        '%Y/%m/%d %H:%M:%S.%f',  # 2025/09/30 12:00:34.1455
        '%Y/%m/%d %H:%M:%S',  # 2025/09/30 12:00:34
        '%Y/%m/%d %H:%M',  # 2025/09/30 12:00
        '%Y/%m/%d',  # 2025/09/30
        '%m/%d/%Y %H:%M:%S.%f',  # 09/30/2025 12:00:34.1455
        '%m/%d/%Y %H:%M:%S',  # 09/30/2025 12:00:34
        '%m/%d/%Y %H:%M',  # 09/30/2025 12:00
        '%m/%d/%Y',  # 09/30/2025
      ]

      for fmt in datetime_formats:
        try:
          return datetime.strptime(value, fmt)
        except ValueError:
          continue

      raise ValueError(f'Value "{value}" for DateAxisRange cannot be converted to datetime.')

    self.min = parse_value(min)
    self.max = parse_value(max)

  def to_dict(self) -> dict[str, str]:
    """Convert DatetimeAxisRange to dictionary format for storage."""
    return {
      'min': self.min.strftime('%Y-%m-%d'),
      'max': self.max.strftime('%Y-%m-%d'),
    }

  def is_valid(self) -> bool:
    """Check if the DatetimeAxisRange object is valid by ensuring all min and max values are set."""
    return self.min is not None and self.max is not None


@dataclass
class FloatAxisRange:
  min: float
  max: float

  def __init__(self, min: str | float | None, max: str | float | None):
    def parse_value(value: str | float | None) -> float:
      if value is None:
        raise ValueError('Value for FloatAxisRange cannot be None.')
      if isinstance(value, float):
        return value
      if isinstance(value, int):
        return float(value)
      if not isinstance(value, str) or value == '':
        raise ValueError(f'Value "{value}" for FloatAxisRange cannot be empty.')

      try:
        return float(value)
      except ValueError:
        raise ValueError(f'Value "{value}" for FloatAxisRange cannot be converted to float.')

    self.min = parse_value(min)
    self.max = parse_value(max)

  def to_dict(self) -> dict[str, float]:
    """Convert FloatAxisRange to dictionary format for storage."""
    return {'min': self.min, 'max': self.max}

  def is_valid(self) -> bool:
    """Check if the FloatAxisRange object is valid by ensuring all min and max values are set."""
    return self.min is not None and self.max is not None


@dataclass
class Zoom:
  x: DatetimeAxisRange
  y: FloatAxisRange

  def __init__(
    self,
    x: DatetimeAxisRange | None = None,
    y: FloatAxisRange | None = None,
    x_min: str | datetime | None = None,
    x_max: str | datetime | None = None,
    y_min: str | float | None = None,
    y_max: str | float | None = None,
  ):
    """Initialize Zoom object.

    Can be initialized either by:
    - Passing DatetimeAxisRange and FloatAxisRange objects: x=DatetimeAxisRange(...), y=FloatAxisRange(...)
    - Passing individual values: x_min, x_max (datetime/str), y_min, y_max (float/str)
    """
    if x is not None and y is not None:
      self.x = x
      self.y = y
    elif x_min is not None and x_max is not None and y_min is not None and y_max is not None:
      self.x = DatetimeAxisRange(min=x_min, max=x_max)
      self.y = FloatAxisRange(min=y_min, max=y_max)
    else:
      raise ValueError(
        'Zoom must be initialized with either (x, y) DatetimeAxisRange/FloatAxisRange objects or'
        + ' (x_min, x_max, y_min, y_max) values.'
      )

  @classmethod
  def from_dict(cls, data: dict[str, Any] | None) -> Self | None:
    """Create Zoom object from dictionary."""
    if not data or not data.get('x') or not data.get('y'):
      return None
    try:
      x_data = data['x']
      y_data = data['y']
      zoom = cls(
        x_min=x_data.get('min'),
        x_max=x_data.get('max'),
        y_min=y_data.get('min'),
        y_max=y_data.get('max'),
      )
      return zoom if zoom.is_valid() else None
    except (ValueError, KeyError, TypeError):
      return None

  def to_dict(self) -> dict[str, dict[str, str | float]]:
    """Convert Zoom to dictionary format for storage in Dash Store."""
    return {'x': self.x.to_dict(), 'y': self.y.to_dict()}

  def is_valid(self) -> bool:
    """Check if the Zoom object is valid by ensuring all x and y values are set."""
    return self.x and self.x.is_valid() and self.y and self.y.is_valid()
