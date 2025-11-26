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
                'Save chart zoom', id='use-chart-zoom-button', size='xs', variant='subtle'
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


# Update Reset button disabled state based on whether current_zoom equals saved_zoom
@callback(
  Output('reset-zoom-button', 'disabled'),
  Input('current-zoom-store', 'data'),
  Input('saved-zoom-store', 'data'),
)
def update_reset_button_state(
  current_zoom: dict[str, dict[str, Any]] | None,
  saved_zoom: dict[str, dict[str, Any]] | None,
):
  """Disable Reset button when current_zoom equals saved_zoom."""
  if not current_zoom or not saved_zoom:
    return False

  # Compare zoom values
  current_x = current_zoom.get('x', {})
  current_y = current_zoom.get('y', {})
  saved_x = saved_zoom.get('x', {})
  saved_y = saved_zoom.get('y', {})

  # Check if all values match
  zoom_equal = (
    current_x.get('min') == saved_x.get('min')
    and current_x.get('max') == saved_x.get('max')
    and current_y.get('min') == saved_y.get('min')
    and current_y.get('max') == saved_y.get('max')
  )

  return zoom_equal


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
def reset_zoom(n_clicks, saved_zoom_data):
  if not n_clicks or not saved_zoom_data:
    raise exceptions.PreventUpdate

  # Reset current_zoom to saved_zoom value
  current_zoom_dict = saved_zoom_data

  # Update controls to match saved_zoom
  x_data = saved_zoom_data.get('x', {})
  y_data = saved_zoom_data.get('y', {})

  return (
    current_zoom_dict,
    x_data.get('min'),
    x_data.get('max'),
    y_data.get('min'),
    y_data.get('max'),
  )


# If the Use Chart Zoom button is pressed, update saved_zoom to current_zoom and update UI controls
@callback(
  Output('saved-zoom-store', 'data'),
  Output('zoom-x-min', 'value', allow_duplicate=True),
  Output('zoom-x-max', 'value', allow_duplicate=True),
  Output('zoom-y-min', 'value', allow_duplicate=True),
  Output('zoom-y-max', 'value', allow_duplicate=True),
  Input('use-chart-zoom-button', 'n_clicks'),
  State('current-zoom-store', 'data'),
  prevent_initial_call=True,
)
def use_chart_zoom(n_clicks, current_zoom_data):
  if not n_clicks or not current_zoom_data:
    raise exceptions.PreventUpdate

  # Update saved_zoom to current_zoom value
  saved_zoom_dict = current_zoom_data

  # Update UI controls to match current_zoom
  x_data = current_zoom_data.get('x', {})
  y_data = current_zoom_data.get('y', {})

  return (
    saved_zoom_dict,
    x_data.get('min'),
    x_data.get('max'),
    y_data.get('min'),
    y_data.get('max'),
  )


# If the zoom is manually changed through the UI controls, change only current_zoom, not saved_zoom
@callback(
  Output('current-zoom-store', 'data', allow_duplicate=True),
  Input('zoom-x-min', 'value'),
  Input('zoom-x-max', 'value'),
  Input('zoom-y-min', 'value'),
  Input('zoom-y-max', 'value'),
  prevent_initial_call=True,
)
def update_current_zoom_from_controls(x_min, x_max, y_min, y_max):
  if x_min is None or x_max is None or y_min is None or y_max is None:
    raise exceptions.PreventUpdate
  # Convert to Zoom object and back to dict for consistency
  zoom = Zoom(x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)
  return zoom.to_dict() if zoom.is_valid() else None
