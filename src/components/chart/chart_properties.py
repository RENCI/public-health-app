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
class AxisRange:
  min: str | None
  max: str | None


@dataclass
class Zoom:
  x: AxisRange
  y: AxisRange
