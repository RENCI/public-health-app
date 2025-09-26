from typing import Any, Callable

import dash_mantine_components as dmc

from .age_group_select import age_group_select
from .annotations_input import annotations_input
from .ensemble_select import ensemble_select
from .location_select import location_select
from .models_select import models_select
from .scenarios_select import scenarios_select
from .target_select import target_select
from .uncertainty_select import uncertainty_select

__all__ = [
  'age_group_select',
  'annotations_input',
  'create_selector_grid_column',
  'ensemble_select',
  'location_select',
  'models_select',
  'scenarios_select',
  'target_select',
  'uncertainty_select',
]


def create_selector_grid_column(
  selector: Callable, initial_values: Any, span: int = 12
) -> dmc.GridCol:
  return dmc.GridCol(
    selector(initial_values),  # Pass as positional argument, not keyword
    style=dict(padding='var(--mantine-spacing-sm)'),
    span=dict(base=span),
  )
