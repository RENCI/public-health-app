"""Application constants loaded at startup."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

# Global variable to store loaded constants
_CONSTANTS: Optional[Dict[str, Any]] = None
_LOCATIONS: Optional[dict[str, tuple[str, int, int]]] = None


def load_constants() -> Dict[str, Any]:
  """Load constants from JSON file."""
  constants_path = Path('src/data/data/constant.json')
  locations_path = Path('src/data/data/locations.json')
  if not constants_path.exists():
    raise FileNotFoundError(f'Constants file not found: {constants_path}')

  with open(constants_path, 'r') as f:
    constants = json.load(f)

  with open(locations_path, 'r') as f:
    locations = {
      record['location_name']: (
        record['location_short_code'],
        record['location_index'],
        record['location_population'],
      )
      for record in pd.read_csv(f).to_dict('records')
    }

  print(f'Loaded constants for pathogen: {constants.get("pathogen", "Unknown")}')
  return constants, locations


def get_constants() -> Dict[str, Any]:
  """Get the loaded constants. Loads them if not already loaded."""
  global _CONSTANTS
  global _LOCATIONS

  CONSTANTS, LOCATIONS = load_constants()

  if _CONSTANTS is None:
    _CONSTANTS = CONSTANTS
  if _LOCATIONS is None:
    _LOCATIONS = LOCATIONS

  return _CONSTANTS


# Convenience functions for common access patterns
def get_pathogen() -> str:
  """Get the current pathogen."""
  return get_constants()['pathogen']


def get_pathogen_display_name() -> str:
  """Get the pathogen display name."""
  return get_constants()['pathogen_display_name']


def get_scenario_name(id: int) -> str:
  """Get scenario ID mappings."""
  return get_constants()['scenario_id'][str(id)]


def get_model_name(id: int) -> str:
  """Get model name mappings."""
  return get_constants()['model_name'][str(id)]


def get_model_id(name: str) -> int:
  """Get model ID mappings."""
  models: dict[str, str] = get_constants()['model_name']
  for model_id, model_name in models.items():
    if model_name == name:
      return int(model_id)
  raise ValueError(f"Model name '{name}' not found")


def get_color_dict() -> Dict[str, str]:
  """Get color mappings for models."""
  return get_constants()['color_dict']


def get_pathogen_color_dict() -> Dict[str, str]:
  """Get color mappings for pathogens."""
  return get_constants()['pathogen_color_dict']


def get_location_data(location: str) -> tuple[str, int, int]:
  """Get the short code for a specific location."""
  return get_constants()['locations'][location]


def get_location_order() -> list[str]:
  """Get the ordered list of locations."""
  return get_constants()['location_order']


def get_model_color(id: int = 1, name: str | None = None) -> str:
  """Get the color for a specific model."""
  colors = get_color_dict()
  return colors.get(name or get_model_name(id), 'rgba(128, 128, 128, 1)')  # Default gray


def get_pathogen_color(pathogen: str = 'RSV') -> str:
  """Get the color for a specific pathogen."""
  colors = get_pathogen_color_dict()
  return colors.get(pathogen, 'rgba(128, 128, 128, 1)')  # Default gray
