from enum import Enum, StrEnum


class Target(StrEnum):
  INCIDENT_HOSPITALIZATION = 'incident_hospitalization'
  CUMULATIVE_HOSPITALIZATION = 'cumulative_hospitalization'


class AgeGroup(Enum):
  ALL = ('0-130', 'all ages')
  UNDER_ONE_YEAR_OLD = ('0-0.99', 'ages 0-1')
  ONE_TO_FOUR_YEARS_OLD = ('1-4', 'ages 1-4')
  FIVE_TO_SIXTY_FOUR_YEARS_OLD = ('5-64', 'ages 5-64')
  SIXTY_FIVE_AND_ABOVE = ('65-130', 'ages 65+')

  def __init__(self, input_value: str, display_value: str):
    self.input_value = input_value
    self.display_value = display_value

  @classmethod
  def from_input_value(cls, value: str) -> 'AgeGroup':
    for member in cls:
      if member.input_value == value:
        return member
    raise ValueError(f'No enum member found for input value: {value}')

  @classmethod
  def from_display_value(cls, value: str) -> 'AgeGroup':
    for member in cls:
      if member.display_value == value:
        return member
    raise ValueError(f'No enum member found for display value: {value}')

  def get_input_value(self) -> str:
    return self.input_value

  def get_display_value(self) -> str:
    return self.display_value


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
