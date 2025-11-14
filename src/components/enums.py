from enum import Enum
from typing import Self


class InputAndDisplayEnum(Enum):
  def __init__(self, display_value: str, input_value: str):
    self.display_value = display_value
    self.input_value = input_value

  def get_display_value(self) -> str:
    return self.display_value

  def get_input_value(self) -> str:
    return self.input_value

  @classmethod
  def from_input_value(cls, value: str) -> Self:
    for member in cls:
      if member.input_value == value:
        return member
    raise ValueError(f'No enum member found for input value: {value}')

  @classmethod
  def from_display_value(cls, value: str) -> Self:
    for member in cls:
      if member.display_value == value:
        return member
    raise ValueError(f'No enum member found for display value: {value}')

  @classmethod
  def display_values(cls) -> list[str]:
    return [member.display_value for member in cls]

  @classmethod
  def input_values(cls) -> list[str]:
    return [member.input_value for member in cls]

  def __hash__(self):
    return hash(self.input_value)

  def __eq__(self, other):
    return isinstance(other, InputAndDisplayEnum) and self.input_value == other.input_value


class Target(InputAndDisplayEnum):
  INCIDENT_HOSPITALIZATION = ('Incident Hospitalization', 'incident_hospitalization')
  CUMULATIVE_HOSPITALIZATION = ('Cumulative Hospitalization', 'cumulative_hospitalization')

  def __init__(self, display_value: str, input_value: str):
    super().__init__(display_value, input_value)


class AgeGroup(InputAndDisplayEnum):
  ALL = ('0-130', 'All ages')
  UNDER_SIXTY_FIVE = ('0-64', 'Ages 0-64')
  SIXTY_FIVE_AND_ABOVE = ('65-130', 'Ages 65+')

  def __init__(self, input_value: str, display_value: str):
    super().__init__(display_value, input_value)


class DataType(Enum):
  SAMPLE = ('sample', 'parquet')
  QUANTILE = ('quantile', 'csv')

  def __init__(self, path_value: str, file_extension: str):
    self.path_value = path_value
    self.file_extension = file_extension

  def get_path_value(self) -> str:
    return self.path_value

  def get_file_extension(self) -> str:
    return self.file_extension

  def __hash__(self):
    return hash(self.path_value)

  def __eq__(self, other):
    return isinstance(other, DataType) and self.path_value == other.path_value


class UncertaintyInterval(Enum):
  NONE = ('None', [])
  FIFTY_PERCENT = ('50%', [(0.25, 0.75)])
  EIGHTY_PERCENT = ('80%', [(0.1, 0.9)])
  NINETY_PERCENT = ('90%', [(0.05, 0.95)])
  NINETY_FIVE_PERCENT = ('95%', [(0.025, 0.975)])
  ALL = ('All', [(0.025, 0.975), (0.05, 0.95), (0.1, 0.9), (0.25, 0.75)])

  def __init__(self, display_value: str, bounds: list[tuple[float, float]]):
    self.display_value = display_value
    self.bounds = bounds

  def get_display_value(self) -> str:
    return self.display_value

  def get_bounds(self) -> list[tuple[float, float]]:
    return self.bounds

  @classmethod
  def from_display_value(cls, value: str) -> Self:
    for member in cls:
      if member.display_value == value:
        return member
    raise ValueError(f'No enum member found for display value: {value}')

  @classmethod
  def from_bounds(cls, bounds: list[tuple[float, float]]) -> Self:
    for member in cls:
      if member.bounds == bounds:
        return member
    raise ValueError(f'No enum member found for bounds: {bounds}')

  @classmethod
  def display_values(cls) -> list[str]:
    return [member.display_value for member in cls]

  @classmethod
  def bounds_values(cls) -> list[str]:
    return [member.bounds for member in cls]

  def __hash__(self):
    return hash(self.display_value)

  def __eq__(self, other):
    return isinstance(other, UncertaintyInterval) and self.display_value == other.display_value
