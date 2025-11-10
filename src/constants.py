"""Application constants loaded at startup."""

import json
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from src.components.enums import UncertaintyInterval
from src.util.colors import replace_opacity

# Global variable to store loaded constants
_CONSTANTS: Optional[dict[str, Any]] = None
_LOCATIONS: Optional[dict[str, tuple[str, str, int]]] = None


def load_constants() -> None:
  """Load constants from JSON file."""
  global _CONSTANTS
  constants_path = Path('src/data/metadata/constant.json')
  if not constants_path.exists():
    raise FileNotFoundError(f'Constants file not found: {constants_path}')

  with open(constants_path, 'r') as f:
    constants = json.load(f)

  _CONSTANTS = constants


def load_locations() -> None:
  """Load the locations."""
  global _LOCATIONS
  locations_path = Path('src/data/metadata/locations.csv')
  if not locations_path.exists():
    raise FileNotFoundError(f'Locations file not found: {locations_path}')

  with open(locations_path, 'r') as f:
    locations = pd.read_csv(f).to_dict('records')
    locations_dict = {
      record['location_name']: (
        record['abbreviation'],
        record['location_id'],
        record['population'],
      )
      for record in locations
    }

  _LOCATIONS = locations_dict


def get_constants() -> dict[str, Any]:
  """Get the loaded constants. Loads them if not already loaded."""
  global _CONSTANTS
  if _CONSTANTS is None:
    load_constants()
  return _CONSTANTS


def get_locations() -> dict[str, tuple[str, int, int]]:
  """Get the loaded locations."""
  global _LOCATIONS
  if _LOCATIONS is None:
    load_locations()
  return _LOCATIONS


def get_location_data(location_name: str) -> tuple[str, int, int]:
  location_data = get_locations().get(location_name.lower().capitalize(), ('', '', 0))
  return (location_data[0], int(location_data[1]), int(location_data[2]))


# Convenience functions for common access patterns
def get_pathogen() -> str:
  """Get the current pathogen."""
  return get_constants().get('pathogen', '')


def get_pathogen_display_name() -> str:
  """Get the pathogen display name."""
  return get_constants().get('pathogen_display_name', '')


def get_scenarios() -> list[dict[str, str]]:
  """Get scenario ID mappings."""
  return get_constants().get('scenarios', [])


def get_scenario_ids() -> list[int]:
  """Get scenario ID mappings."""
  return [scenario['id'] for scenario in get_scenarios()]


def get_scenario_id(name: str) -> int | None:
  """Get scenario ID mappings."""
  return [scenario['id'] for scenario in get_scenarios() if scenario['name'] == name][0]


def get_scenario_names() -> list[str]:
  """Get scenario name mappings."""
  return [scenario['name'] for scenario in get_scenarios()]


def get_scenario_name(id: int) -> str:
  """Get scenario ID mappings."""
  return [scenario['name'] for scenario in get_scenarios() if scenario['id'] == id][0]


def get_models() -> list[dict[str, str]]:
  """Get model name mappings."""
  return get_constants().get('models', [])


def get_model_names() -> list[str]:
  """Get model name mappings."""
  return [model['name'] for model in get_models()]


def get_model_name(id: int) -> str:
  """Get model name mappings."""
  return [model['name'] for model in get_models() if model['id'] == id][0]


def get_model_id(name: str) -> int:
  """Get model ID mappings."""
  return [model['id'] for model in get_models() if model['name'] == name][0]


def get_model_colors() -> dict[str, str]:
  """Get color mappings for models."""
  return {model['name']: model['color'] for model in get_models()}


def get_model_color_by_id(id: int = 1) -> str:
  """Get the color for a specific model."""
  return [model['color'] for model in get_models() if model['id'] == id][0]


def get_model_color_by_name(name: str = 'Ensemble_LOP') -> str:
  """Get the color for a specific model."""
  return [model['color'] for model in get_models() if model['name'] == name][0]


def get_pathogen_colors() -> dict[str, str]:
  """Get color mappings for pathogens."""
  return get_constants().get('pathogen_colors', [])


def get_pathogen_color(pathogen: str = 'RSV') -> str:
  """Get the color for a specific pathogen."""
  return get_pathogen_colors().get(pathogen, 'rgba(128, 128, 128, 1)')  # Default gray


def get_location_data(location: str) -> tuple[str, int, int]:
  """Get the short code for a specific location."""
  location = location.lower().capitalize()
  return get_locations().get(location, ('', 0, 0))


def get_location_order() -> list[str]:
  """Get the ordered list of locations."""
  return get_constants().get('location_order', [])


def get_uncertainty_interval_opacities() -> dict[UncertaintyInterval, float]:
  """Get the opacity mappings for uncertainty intervals."""
  return {
    UncertaintyInterval.NINETY_FIVE_PERCENT: 0.2,
    UncertaintyInterval.NINETY_PERCENT: 0.3,
    UncertaintyInterval.EIGHTY_PERCENT: 0.4,
    UncertaintyInterval.FIFTY_PERCENT: 0.5,
  }


def get_uncertainty_interval_opacity(uncertainty_interval: UncertaintyInterval) -> float:
  """Get the opacity for a specific uncertainty interval."""
  return get_uncertainty_interval_opacities()[uncertainty_interval]


def get_model_color_with_uncertainty_interval(
  model_color: str,
  uncertainty_interval: UncertaintyInterval = UncertaintyInterval.NINETY_FIVE_PERCENT,
) -> str:
  """Get the model color with the opacity for a specific uncertainty interval. Defaults to 95%."""
  return replace_opacity(model_color, get_uncertainty_interval_opacity(uncertainty_interval))
