from typing import Any
import copy
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import Input, Output, State, callback, exceptions

from src.components.chart import Chart, ChartControls, Zoom, chart_manager
from src.util import any_are_none


def zoom_control(value: Zoom | None = None) -> dmc.Stack:
  if value is None:
    x_min = '2025-01-01'
    x_max = '2026-06-30'
    y_min = 0
    y_max = 65_000
  else:
    x_min = value.x.min
    x_max = value.x.max
    y_min = value.y.min
    y_max = value.y.max

  return dmc.Stack(
    children=[
      dmc.Flex(
        [
          dmc.Text('Zoom', size='md'),
          dmc.Group(
            [
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
  Output('chart-controls-store', 'data', allow_duplicate=True),
  Output('zoom-x-min', 'value', allow_duplicate=True),
  Output('zoom-x-max', 'value', allow_duplicate=True),
  Output('zoom-y-min', 'value', allow_duplicate=True),
  Output('zoom-y-max', 'value', allow_duplicate=True),
  Input('save-chart-zoom-button', 'n_clicks'),
  State('graph', 'relayoutData'),
  State('chart-controls-store', 'data'),
  prevent_initial_call=True,
)
def save_current_chart_zoom(
  n_clicks: int,
  relayout_data: dict[str, Any] | None,
  current_chart_controls: dict[str, Any] | None,
) -> tuple[dict[str, Any], str | None, str | None, float | None, float | None]:
  """Save current chart zoom to saved_zoom when the Save Chart Zoom button is pressed."""
  if any_are_none(n_clicks, relayout_data, current_chart_controls, log_result=True):
    raise exceptions.PreventUpdate

  current_zoom = Chart.calculate_zoom_from_relayout(relayout_data)
  if current_zoom is None:
    print('Could not calculate current zoom from relayout data')
    raise exceptions.PreventUpdate

  new_chart_controls = copy.deepcopy(current_chart_controls)
  new_chart_controls['saved_zoom'] = current_zoom.to_dict()
  return (
    new_chart_controls,
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
  State('chart-controls-store', 'data'),
  prevent_initial_call=True,
)
def update_current_zoom_from_ui_controls(
  x_min: str | None,
  x_max: str | None,
  y_min: float | None,
  y_max: float | None,
  current_chart_controls: dict[str, Any] | None,
) -> go.Figure:
  """Update current_zoom, but not saved_zoom, when the zoom is manually changed through the UI controls."""
  if any_are_none(x_min, x_max, y_min, y_max, current_chart_controls, log_result=True):
    raise exceptions.PreventUpdate

  chart_controls = ChartControls.from_dict(current_chart_controls)
  current_zoom = Zoom(x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)
  chart = chart_manager.get_chart(chart_controls)
  chart.update_current_zoom(current_zoom)
  return chart.get_fig()
