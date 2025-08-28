from enum import Enum, StrEnum

class Target(Enum):
  INCIDENT_HOSPITALIZATION = "inc hosp"
  CUMULATIVE_HOSPITALIZATION = "cum hosp"

class AgeGroupInput(StrEnum):
  ALL = "0-130"
  UNDER_ONE_YEAR_OLD = "0-0.99"
  ONE_TO_FOUR_YEARS_OLD = "1-4"
  FIVE_TO_SIXTY_FOUR_YEARS_OLD = "5-64"
  SIXTY_FIVE_AND_ABOVE = "65-130"

class AgeGroup(StrEnum):
  ALL = "all ages"
  UNDER_ONE_YEAR_OLD = "ages 0-1"
  ONE_TO_FOUR_YEARS_OLD = "ages 1-4"
  FIVE_TO_SIXTY_FOUR_YEARS_OLD = "ages 5-64"
  SIXTY_FIVE_AND_ABOVE = "ages 65+"