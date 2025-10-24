from typing import Any

import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import Input, Output, State, callback, dcc, exceptions, html

from src.components.chart import ChartControls
from src.components.chart_instance_manager import ChartInstanceManager

from .controls import (
  age_group_select,
  annotations_control,
  certainty_select,
  location_select,
  models_select,
  scenarios_select,
  target_select,
  zoom_control,
)

# Global instance of the chart manager
chart_manager = ChartInstanceManager()


default_control_values = dict(
  plot_type='line',
  round_num=19,
  scenario_names=['A-2023-10-27', 'B-2023-10-27'],
  model_names=['Ensemble'],
  location_name='US',
  target='incident_hospitalization',
  x_axis='target_end_date',
  y_axis='value',
  x_start_date='2025-01-01',
  age_group='0-130',
  certainty_percent='95%',
  zoom=dict(
    x=dict(min='2025-01-01', max='2026-06-30'),
    y=dict(min=0, max=65_000),
  ),
  annotations=None,
)


def visualization_editor(control_values=None, show_controls=True):
  controls = {**default_control_values, **(control_values or {})}

  init_plot_type: str = controls['plot_type']
  init_round_num: int = controls['round_num']
  init_scenario_names: list[str] = controls['scenario_names']
  init_model_names: list[str] = controls['model_names']
  init_location_name: str = controls['location_name']
  init_target: str = controls['target']
  init_age_group: str = controls['age_group']
  if 'x_start_date' in controls:
    init_x_start_date: str | None = controls['x_start_date']
  else:
    init_x_start_date = None
  init_x_axis: str = controls['x_axis']
  init_y_axis: str = controls['y_axis']
  init_certainty_percent: str | None = controls['certainty_percent']
  init_zoom: dict[str, dict[str, Any]] | None = controls['zoom']
  init_annotations: list[dict[str, Any]] | None = controls['annotations']

  figure_control_values = dict(
    plot_type=init_plot_type,
    round_num=init_round_num,
    scenario_names=init_scenario_names,
    model_names=init_model_names,
    location_name=init_location_name,
    target=init_target,
    age_group=init_age_group,
    x_axis=init_x_axis,
    y_axis=init_y_axis,
    x_start_date=init_x_start_date,
    zoom=init_zoom,
    annotations=init_annotations,
    certainty_percent=init_certainty_percent,
  )

  chart_controls_store = dcc.Store(
    id='chart-controls-store', storage_type='local', data=figure_control_values
  )
  chart_extent_store = dcc.Store(id='chart-extent-store', storage_type='local')

  chart_controls = ChartControls(**figure_control_values)

  # Get or create chart instance using the manager
  chart = chart_manager.get_chart(chart_controls)
  figure = chart.get_fig() if chart else go.Figure()
  graph = dcc.Graph(id='graph', figure=figure)

  empty_figure_container = html.Div(
    id='insight-visualization-figure',
    children=graph,
    style={'min-height': '45vh'},
  )

  if not chart:
    return empty_figure_container

  if not show_controls:
    return graph

  return dmc.Grid(
    [
      dmc.GridCol(
        [
          chart_controls_store,
          chart_extent_store,
          graph,
        ],
        id='visualization-column',
        span=dict(base=12, xl=8),
        style={'display': 'flex', 'flexDirection': 'column'},
      ),
      dmc.GridCol(
        dmc.Stack(
          [
            dmc.Card(
              dmc.Grid(
                [
                  dmc.GridCol(scenarios_select(value=init_scenario_names), span=dict(base=12)),
                  dmc.GridCol(models_select(value=init_model_names), span=dict(base=12)),
                  dmc.GridCol(location_select(value=init_location_name), span=dict(base=12, sm=6)),
                  dmc.GridCol(target_select(value=init_target), span=dict(base=12, sm=6)),
                  dmc.GridCol(age_group_select(value=init_age_group), span=dict(base=12, sm=6)),
                  dmc.GridCol(certainty_select(value=init_certainty_percent), span=dict(base=12, sm=6)),
                ],
              ),
              variant='soft',
            ),
            dmc.Card(
              zoom_control(value=init_zoom),
              variant='soft',
            ),
            dmc.Card(
              annotations_control(value=init_annotations),
              variant='soft',
            ),
          ],
          gap='md',
        ),
        id='controls-column',
        span=dict(base=12, xl=4),
      ),
    ],
    mb=12,
  )


@callback(
  Output('graph', 'figure'),
  Input('chart-controls-store', 'data'),
  # prevent_initial_call=True,
)
def update_graph_figure(
  controls: dict[str, Any],
):
  if not controls:
    raise exceptions.PreventUpdate

  try:
    chart_controls = ChartControls(
      plot_type=controls['plot_type'],
      round_num=controls['round_num'],
      pathogen='covid',
      scenario_names=controls['scenario_names'],
      model_names=controls['model_names'],
      location_name=controls['location_name'],
      target=controls['target'],
      age_group=controls['age_group'],
      x_axis=controls['x_axis'],
      y_axis=controls['y_axis'],
      x_start_date=controls['x_start_date'],
      certainty_percent=controls['certainty_percent'],
      zoom=controls['zoom'],
      annotations=controls['annotations'],
    )

    # Get or create chart instance using the manager
    chart = chart_manager.get_chart(chart_controls)

    if not chart:
      raise Exception('Chart not found')

    return chart.get_fig()
  except Exception as e:
    print(f'Error updating chart: {e}')
    import traceback

    traceback.print_exc()
    return go.Figure(layout=go.Layout(title='Error loading chart'))


@callback(
  Output('chart-controls-store', 'data'),
  Input('scenarios-select', 'value'),
  Input('models-select', 'value'),
  Input('location-select', 'value'),
  Input('target-select', 'value'),
  Input('age-group-select', 'value'),
  Input('certainty-select', 'value'),
  Input('zoom-store', 'data'),
  Input('annotations-store', 'data'),
  Input('graph', 'relayoutData'),
  State('chart-controls-store', 'data'),
  prevent_initial_call=True,
)
def update_chart_controls(
  scenarios,
  models,
  location,
  target,
  age_group,
  certainty,
  zoom,
  annotations,
  relayout,
  current_chart_controls: dict[str, Any],
):
  if not (
    scenarios
    and models
    and location
    and target
    and age_group
    and certainty
    and zoom
    and annotations
    and relayout
    and current_chart_controls
  ):
    raise exceptions.PreventUpdate

  new_zoom = dict(
    x={'min': relayout.get('xaxis.range[0]'), 'max': relayout.get('xaxis.range[1]')},
    y={'min': relayout.get('yaxis.range[0]'), 'max': relayout.get('yaxis.range[1]')},
  )
  new_chart_controls = dict(
    scenario_names=scenarios,
    model_names=models,
    location_name=location,
    target=target,
    age_group=age_group,
    certainty_percent=certainty,
    zoom=new_zoom,
    annotations=annotations,
  )
  return {**current_chart_controls, **new_chart_controls}


# TODO: Add this back in when we have a way to sync the zoom store with the chart controls store
@callback(
  Output('zoom-x-min', 'value'),
  Output('zoom-x-max', 'value'),
  Output('zoom-y-min', 'value'),
  Output('zoom-y-max', 'value'),
  Input('use-chart-zoom-button', 'n_clicks'),
  State('chart-extent-store', 'data'),
  prevent_initial_call=True,
)
def apply_current_zoom(n_clicks, current_zoom):
  if not n_clicks or not current_zoom:
    raise exceptions.PreventUpdate

  return (
    current_zoom['x'].get('min'),
    current_zoom['x'].get('max'),
    current_zoom['y'].get('min'),
    current_zoom['y'].get('max'),
  )
