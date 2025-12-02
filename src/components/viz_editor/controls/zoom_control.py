import copy
from typing import Any

import dash_mantine_components as dmc
from dash import Input, Output, State, callback, exceptions

from src.components.chart import Zoom


def zoom_control(value: dict[str, Any] | None = None):
  x_data = value.get('x', {}) if value else {}
  y_data = value.get('y', {}) if value else {}

  x_min = x_data.get('min') or '2025-01-01'
  x_max = x_data.get('max') or '2026-06-30'
  y_min = y_data.get('min') if y_data.get('min') is not None else 0
  y_max = y_data.get('max') if y_data.get('max') is not None else 65_000

  return dmc.Stack(
    children=[
      dmc.Flex(
        [
          dmc.Text('Zoom', size='md'),
          dmc.Group(
            [
              dmc.Button(
                'Reset', id='reset-zoom-button', size='xs', variant='subtle', disabled=False
              ),
              dmc.Button(
                'Save chart zoom', id='save-chart-zoom-button', size='xs', variant='subtle'
              ),
            ],
            gap='xs',
          ),
        ],
        justify='space-between',
      ),
      dmc.Divider(),
      dmc.Grid(
        [
          dmc.GridCol(
            dmc.DateInput(id='zoom-x-min', label='X min', value=x_min),
            span=dict(base=12, md=6, sm=6),
          ),
          dmc.GridCol(
            dmc.DateInput(id='zoom-x-max', label='X max', value=x_max),
            span=dict(base=12, md=6, sm=6),
          ),
          dmc.GridCol(
            dmc.NumberInput(id='zoom-y-min', label='Y min', value=y_min, step=100),
            span=dict(base=12, md=6, sm=6),
          ),
          dmc.GridCol(
            dmc.NumberInput(id='zoom-y-max', label='Y max', value=y_max, step=100),
            span=dict(base=12, md=6, sm=6),
          ),
        ],
      ),
    ]
  )


@callback(
  Output('saved-zoom-store', 'data'),
  Output('zoom-x-min', 'value'),
  Output('zoom-x-max', 'value'),
  Output('zoom-y-min', 'value'),
  Output('zoom-y-max', 'value'),
  Input('current-zoom-store', 'data'),
  State('saved-zoom-store', 'data'),
)
def initialize_saved_zoom_and_zoom_controls(
  current_zoom_data: dict[str, dict[str, Any]] | None,
  saved_zoom_data: dict[str, dict[str, Any]] | None,
):
  """
  Initialize zoom UI controls from current_zoom and saved_zoom.
  If one of current_zoom or saved_zoom is provided, but the other is not, set the other to the provided value.
  If neither are provided, use default values.
  """
  if current_zoom_data is None and saved_zoom_data is None:
    raise exceptions.PreventUpdate

  current_zoom = None
  saved_zoom = None

  if current_zoom_data is not None:
    current_zoom = Zoom.from_dict(current_zoom_data)
  if saved_zoom_data is not None:
    saved_zoom = Zoom.from_dict(saved_zoom_data)

  if current_zoom is not None and saved_zoom is None:
    return (
      current_zoom.to_dict(),
      current_zoom.x.min,
      current_zoom.x.max,
      current_zoom.y.min,
      current_zoom.y.max,
    )
  else:
    return (
      saved_zoom.to_dict(),
      saved_zoom.x.min,
      saved_zoom.x.max,
      saved_zoom.y.min,
      saved_zoom.y.max,
    )


@callback(
  Output('reset-zoom-button', 'disabled'),
  Input('current-zoom-store', 'data'),
  Input('saved-zoom-store', 'data'),
)
def update_reset_button_state(
  current_zoom: dict[str, dict[str, Any]] | None,
  saved_zoom: dict[str, dict[str, Any]] | None,
):
  """Disable Reset button when current_zoom is equal to saved_zoom."""
  if current_zoom is None:
    return False
  if saved_zoom is None:
    return True

  return Zoom.from_dict(current_zoom) == Zoom.from_dict(saved_zoom)


# If the Reset button is pressed, reset current_zoom to saved_zoom and update UI controls
@callback(
  Output('current-zoom-store', 'data', allow_duplicate=True),
  Output('zoom-x-min', 'value', allow_duplicate=True),
  Output('zoom-x-max', 'value', allow_duplicate=True),
  Output('zoom-y-min', 'value', allow_duplicate=True),
  Output('zoom-y-max', 'value', allow_duplicate=True),
  Input('reset-zoom-button', 'n_clicks'),
  State('saved-zoom-store', 'data'),
  prevent_initial_call=True,
)
def reset_zoom(n_clicks: int, saved_zoom_data: dict[str, dict[str, Any]] | None):
  """Reset current_zoom to saved_zoom value when the Reset button is pressed."""
  if not n_clicks or not saved_zoom_data:
    raise exceptions.PreventUpdate
  current_zoom = Zoom.from_dict(saved_zoom_data)
  if current_zoom is None:
    raise exceptions.PreventUpdate
  return (
    current_zoom.to_dict(),
    current_zoom.x.min,
    current_zoom.x.max,
    current_zoom.y.min,
    current_zoom.y.max,
  )


# If the Save Chart Zoom button is pressed, update saved_zoom to current_zoom and update UI controls
@callback(
  Output('saved-zoom-store', 'data', allow_duplicate=True),
  Output('zoom-x-min', 'value', allow_duplicate=True),
  Output('zoom-x-max', 'value', allow_duplicate=True),
  Output('zoom-y-min', 'value', allow_duplicate=True),
  Output('zoom-y-max', 'value', allow_duplicate=True),
  Input('save-chart-zoom-button', 'n_clicks'),
  State('current-zoom-store', 'data'),
  prevent_initial_call=True,
)
def save_current_chart_zoom(n_clicks: int, current_zoom_data: dict[str, dict[str, Any]] | None):
  if not n_clicks or not current_zoom_data:
    raise exceptions.PreventUpdate

  current_zoom = Zoom.from_dict(current_zoom_data)
  if current_zoom is None:
    raise exceptions.PreventUpdate

  saved_zoom = copy.deepcopy(current_zoom)
  if saved_zoom is None:
    raise exceptions.PreventUpdate

  return (
    saved_zoom.to_dict(),
    saved_zoom.x.min,
    saved_zoom.x.max,
    saved_zoom.y.min,
    saved_zoom.y.max,
  )


@callback(
  Output('current-zoom-store', 'data', allow_duplicate=True),
  Input('zoom-x-min', 'value'),
  Input('zoom-x-max', 'value'),
  Input('zoom-y-min', 'value'),
  Input('zoom-y-max', 'value'),
  prevent_initial_call=True,
)
def update_current_zoom_from_controls(
  x_min: str | None, x_max: str | None, y_min: float | None, y_max: float | None
):
  """Update current_zoom, but not saved_zoom, when the zoom is manually changed through the UI controls."""
  if x_min is None or x_max is None or y_min is None or y_max is None:
    raise exceptions.PreventUpdate
  try:
    current_zoom = Zoom(x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)
    return current_zoom.to_dict()
  except ValueError:
    return None
