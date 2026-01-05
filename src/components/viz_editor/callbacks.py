from typing import Any

import plotly.graph_objects as go
from dash import Input, Output, State, callback, exceptions

from src.components.chart import ChartControls
from src.components.chart.chart_instance_manager import ChartInstanceManager
from src.util.constants import DEFAULT_CONTROL_VALUES

from .controls import (
  age_group_select,
  annotations_control,
  layout_select,
  location_select,
  models_select,
  scenarios_select,
  target_select,
  uncertainty_interval_select,
  zoom_control,
)

# Global instance of the chart manager
chart_manager = ChartInstanceManager()


@callback(
  Output('graph', 'figure'),
  Input('chart-controls-store', 'data'),
  # prevent_initial_call=True,
)
def update_graph_figure(
  current_chart_controls: dict[str, Any],
):
  if not current_chart_controls:
    raise exceptions.PreventUpdate  
  
  try:
    chart_controls = ChartControls.from_dict({**DEFAULT_CONTROL_VALUES, **current_chart_controls})

    # Get or create chart instance using the manager
    chart = chart_manager.get_chart(chart_controls)

    if not chart:
      raise Exception('Chart not found')

    return chart.get_fig()
  except Exception as e:
    import traceback

    print(traceback.print_exception(e))
    return go.Figure(layout=go.Layout(title='Error loading chart'))


@callback(
  Output('chart-controls-store', 'data', allow_duplicate=True),
  Input('theme-store', 'data'),
  Input('scenarios-select', 'value'),
  Input('models-select', 'value'),
  Input('chart-layout-select', 'value'),
  Input('location-select', 'value'),
  Input('target-select', 'value'),
  Input('age-group-select', 'value'),
  Input('uncertainty-interval-select', 'value'),
  Input('zoom-store', 'data'),
  Input('annotations-store', 'data'),
  Input('graph', 'relayoutData'),
  Input('initial-page-load-chart-controls-store', 'data'),
  State('chart-controls-store', 'data'),
  prevent_initial_call=True,
)
def update_chart_controls(
  theme: str,
  scenario_ids: list[str],
  model_names: list[str],
  chart_layout: str,
  location_name: str,
  target: str,
  age_group: str,
  uncertainty_interval: str | None,
  zoom: dict[str, dict[str, Any]] | None,
  annotations: list[dict[str, Any]] | None,
  relayout: dict[str, Any] | None,
  initial_chart_controls: dict[str, Any] | None,
  current_chart_controls: dict[str, Any] | None,
):
  if not (scenario_ids and model_names and location_name and target and age_group):
    raise exceptions.PreventUpdate

  new_zoom = None
  if relayout:
    x_range_min = None
    x_range_max = None
    y_range_min = None
    y_range_max = None

    for key in relayout.keys():
      if key.startswith('xaxis') and '.range' in key:
        if key.endswith('.range[0]'):
          x_range_min = relayout.get(key)
          range_key_1 = key.replace('.range[0]', '.range[1]')
          x_range_max = relayout.get(range_key_1)
        elif key.endswith('.range') and isinstance(relayout.get(key), list):
          x_range = relayout.get(key)
          if x_range and len(x_range) >= 2:
            x_range_min = x_range[0]
            x_range_max = x_range[1]
      elif key.startswith('yaxis') and '.range' in key:
        if key.endswith('.range[0]'):
          y_range_min = relayout.get(key)
          range_key_1 = key.replace('.range[0]', '.range[1]')
          y_range_max = relayout.get(range_key_1)
        elif key.endswith('.range') and isinstance(relayout.get(key), list):
          y_range = relayout.get(key)
          if y_range and len(y_range) >= 2:
            y_range_min = y_range[0]
            y_range_max = y_range[1]

    if (
      x_range_min is not None
      and x_range_max is not None
      and y_range_min is not None
      and y_range_max is not None
    ):
      new_zoom = {
        'x': {
          'min': x_range_min,
          'max': x_range_max,
        },
        'y': {
          'min': y_range_min,
          'max': y_range_max,
        },
      }

  new_chart_controls = dict(
    theme=theme,
    scenario_ids=[int(scenario_id) for scenario_id in scenario_ids],
    model_names=model_names,
    chart_layout=chart_layout,
    location_name=location_name,
    target=target,
    age_group=age_group,
    uncertainty_interval=uncertainty_interval,
    zoom=new_zoom,
    annotations=annotations,
  )
  # initial_chart_controls must come after current_chart_controls;
  # see initial_page_load_chart_controls_store comment above for more details
  return {
    **DEFAULT_CONTROL_VALUES,
    **current_chart_controls,
    **initial_chart_controls,
    **new_chart_controls,
  }


@callback(
  Output('chart-extent-store', 'data'),
  Input('graph', 'relayoutData'),
)
def sync_zoom_store(relayout):
  if not relayout:
    raise exceptions.PreventUpdate

  x_range_min = None
  x_range_max = None
  y_range_min = None
  y_range_max = None

  for key in relayout.keys():
    if key.startswith('xaxis') and '.range' in key:
      if key.endswith('.range[0]'):
        x_range_min = relayout.get(key)
        range_key_1 = key.replace('.range[0]', '.range[1]')
        x_range_max = relayout.get(range_key_1)
      elif key.endswith('.range') and isinstance(relayout.get(key), list):
        x_range = relayout.get(key)
        if x_range and len(x_range) >= 2:
          x_range_min = x_range[0]
          x_range_max = x_range[1]
    elif key.startswith('yaxis') and '.range' in key:
      if key.endswith('.range[0]'):
        y_range_min = relayout.get(key)
        range_key_1 = key.replace('.range[0]', '.range[1]')
        y_range_max = relayout.get(range_key_1)
      elif key.endswith('.range') and isinstance(relayout.get(key), list):
        y_range = relayout.get(key)
        if y_range and len(y_range) >= 2:
          y_range_min = y_range[0]
          y_range_max = y_range[1]

  if (
    x_range_min is not None
    and x_range_max is not None
    and y_range_min is not None
    and y_range_max is not None
  ):
    return {
      'x': {
        'min': x_range_min,
        'max': x_range_max,
      },
      'y': {
        'min': y_range_min,
        'max': y_range_max,
      },
    }
  else:
    return None


@callback(
  Output('zoom-x-min', 'value'),
  Output('zoom-x-max', 'value'),
  Output('zoom-y-min', 'value'),
  Output('zoom-y-max', 'value'),
  Input('chart-extent-store', 'data'),
  prevent_initial_call=True,
)
def apply_current_zoom(current_zoom):
  if not current_zoom:
    raise exceptions.PreventUpdate

  return (
    current_zoom['x'].get('min'),
    current_zoom['x'].get('max'),
    current_zoom['y'].get('min'),
    current_zoom['y'].get('max'),
  )
