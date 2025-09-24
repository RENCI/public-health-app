"""Application constants loaded at startup."""

import json
from pathlib import Path
from typing import Any, Optional

import pandas as pd

# Global variable to store loaded constants
_CONSTANTS: Optional[dict[str, Any]] = None
_LOCATIONS: Optional[dict[str, tuple[str, int, int]]] = None


def load_constants() -> None:
  """Load constants from JSON file."""
  global _CONSTANTS
  constants_path = Path('src/data/metadata/constant.json')
  if not constants_path.exists():
    raise FileNotFoundError(f'Constants file not found: {constants_path}')

  with open(constants_path, 'r') as f:
    constants = json.load(f)

  _CONSTANTS = constants
  print('Loaded constants')


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
        record['location'],
        record['population'],
      )
      for record in locations
    }

  _LOCATIONS = locations_dict
  print('Loaded locations')


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


# Convenience functions for common access patterns
def get_pathogen() -> str:
  """Get the current pathogen."""
  return get_constants().get('pathogen', '')


def get_pathogen_display_name() -> str:
  """Get the pathogen display name."""
  return get_constants().get('pathogen_display_name', '')


def get_scenario_name(id: int) -> str:
  """Get scenario ID mappings."""
  scenario_ids = get_constants().get('scenario_name', {})
  return scenario_ids.get(str(id), '')


def get_models() -> dict[str, str]:
  """Get model name mappings."""
  return get_constants().get('model_name', {})


def get_model_names() -> list[str]:
  """Get model name mappings."""
  return list(get_models().values())


def get_model_name(id: int) -> str:
  """Get model name mappings."""
  model_names = get_models()
  return model_names.get(str(id), '')


def get_model_id(name: str) -> int:
  """Get model ID mappings."""
  models: dict[str, str] = get_models()
  for model_id, model_name in models.items():
    if model_name == name:
      return int(model_id)
  raise ValueError(f"Model name '{name}' not found")


def get_model_colors() -> dict[str, str]:
  """Get color mappings for models."""
  return get_models().get('model_color', {})


def get_model_color(id: int = 1, name: str | None = None) -> str:
  """Get the color for a specific model."""
  colors = get_model_colors()
  return colors.get(name or get_model_name(id), 'rgba(128, 128, 128, 1)')  # Default gray


def get_pathogen_colors() -> dict[str, str]:
  """Get color mappings for pathogens."""
  return get_constants().get('pathogen_color', {})


def get_pathogen_color(pathogen: str = 'RSV') -> str:
  """Get the color for a specific pathogen."""
  colors = get_pathogen_colors()
  return colors.get(pathogen, 'rgba(128, 128, 128, 1)')  # Default gray


def get_location_data(location: str) -> tuple[str, int, int]:
  """Get the short code for a specific location."""
  location = location.lower().capitalize()
  return get_locations().get(location, ('', 0, 0))


def get_location_order() -> list[str]:
  """Get the ordered list of locations."""
  return get_constants().get('location_order', [])
