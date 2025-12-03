from typing import Any

import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import Input, Output, State, callback, exceptions

from src.components.chart import Chart, Zoom


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
  Input('graph', 'relayoutData'),
)
def initialize_saved_zoom_and_zoom_controls(
  relayout_data: dict[str, Any] | None,
):
  """
  Initialize zoom UI controls from relayoutData.
  """
  if relayout_data is None:
    raise exceptions.PreventUpdate

  current_zoom = Chart.calculate_zoom_from_relayout(relayout_data)
  if current_zoom is None:
    raise exceptions.PreventUpdate

  return (
    current_zoom.to_dict(),
    current_zoom.x.min,
    current_zoom.x.max,
    current_zoom.y.min,
    current_zoom.y.max,
  )


@callback(
  Output('reset-zoom-button', 'disabled'),
  Input('graph', 'relayoutData'),
  State('saved-zoom-store', 'data'),
)
def update_reset_button_state(
  relayout_data: dict[str, Any] | None,
  saved_zoom_data: dict[str, dict[str, Any]] | None,
):
  """Disable Reset button when current_zoom is equal to saved_zoom."""
  if relayout_data is None:
    return True
  if saved_zoom_data is None:
    return True
  current_zoom = Chart.calculate_zoom_from_relayout(relayout_data)
  if current_zoom is None:
    return True
  saved_zoom = Zoom.from_dict(saved_zoom_data)
  if saved_zoom is None:
    raise exceptions.PreventUpdate

  return current_zoom == saved_zoom


@callback(
  Output('graph', 'figure', allow_duplicate=True),
  Output('zoom-x-min', 'value', allow_duplicate=True),
  Output('zoom-x-max', 'value', allow_duplicate=True),
  Output('zoom-y-min', 'value', allow_duplicate=True),
  Output('zoom-y-max', 'value', allow_duplicate=True),
  Input('reset-zoom-button', 'n_clicks'),
  State('saved-zoom-store', 'data'),
  State('graph', 'figure'),
  prevent_initial_call=True,
)
def reset_zoom(
  n_clicks: int,
  saved_zoom_data: dict[str, dict[str, Any]] | None,
  current_figure: dict[str, Any] | go.Figure,
):
  """Reset current chart zoom and UI controls to saved_zoom value when the Reset button is pressed."""
  if not n_clicks or saved_zoom_data is None:
    raise exceptions.PreventUpdate

  if current_figure is None:
    raise exceptions.PreventUpdate

  figure = go.Figure(current_figure) if isinstance(current_figure, dict) else current_figure
  figure.update_xaxes(range=[saved_zoom_data['x']['min'], saved_zoom_data['x']['max']])
  figure.update_yaxes(range=[saved_zoom_data['y']['min'], saved_zoom_data['y']['max']])

  return (
    figure,
    saved_zoom_data['x']['min'],
    saved_zoom_data['x']['max'],
    saved_zoom_data['y']['min'],
    saved_zoom_data['y']['max'],
  )


@callback(
  Output('saved-zoom-store', 'data', allow_duplicate=True),
  Output('zoom-x-min', 'value', allow_duplicate=True),
  Output('zoom-x-max', 'value', allow_duplicate=True),
  Output('zoom-y-min', 'value', allow_duplicate=True),
  Output('zoom-y-max', 'value', allow_duplicate=True),
  Input('save-chart-zoom-button', 'n_clicks'),
  State('graph', 'relayoutData'),
  prevent_initial_call=True,
)
def save_current_chart_zoom(n_clicks: int, relayout_data: dict[str, Any] | None):
  """Save current chart zoom to saved_zoom when the Save Chart Zoom button is pressed."""
  if not n_clicks or relayout_data is None:
    raise exceptions.PreventUpdate

  current_zoom = Chart.calculate_zoom_from_relayout(relayout_data)
  if current_zoom is None:
    raise exceptions.PreventUpdate

  return (
    current_zoom.to_dict(),
    current_zoom.x.min,
    current_zoom.x.max,
    current_zoom.y.min,
    current_zoom.y.max,
  )


@callback(
  Output('graph', 'figure', allow_duplicate=True),
  Input('zoom-x-min', 'value'),
  Input('zoom-x-max', 'value'),
  Input('zoom-y-min', 'value'),
  Input('zoom-y-max', 'value'),
  State('graph', 'figure'),
  prevent_initial_call=True,
)
def update_current_zoom_from_controls(
  x_min: str | None,
  x_max: str | None,
  y_min: float | None,
  y_max: float | None,
  current_figure: dict[str, Any] | go.Figure,
):
  """Update current_zoom, but not saved_zoom, when the zoom is manually changed through the UI controls."""
  if x_min is None or x_max is None or y_min is None or y_max is None:
    raise exceptions.PreventUpdate

  if current_figure is None:
    raise exceptions.PreventUpdate

  try:
    current_zoom = Zoom(x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)
    figure = go.Figure(current_figure) if isinstance(current_figure, dict) else current_figure
    figure.update_xaxes(range=[current_zoom.x.min, current_zoom.x.max])
    figure.update_yaxes(range=[current_zoom.y.min, current_zoom.y.max])
    return figure
  except ValueError:
    raise exceptions.PreventUpdate
