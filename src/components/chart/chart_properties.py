from abc import ABC
from dataclasses import asdict
from datetime import datetime
from enum import StrEnum
from typing import Any, Self

from src.constants import (
  get_locations,
  get_model_color_by_id,
  get_model_id,
  get_model_name,
  get_scenario_id,
  get_scenario_name,
)


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
