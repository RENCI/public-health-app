from typing import Any

import dash_mantine_components as dmc
from dash import Input, Output, State, callback, dcc, exceptions, html

from src.components.chart import Chart, ChartControls, PlotType

from .controls import (
  age_group_select,
  annotations_input,
  location_select,
  models_select,
  scenarios_select,
  target_select,
  uncertainty_select,
  zoom_control,
)

available_rounds = [19]
current_round = 19

default_control_values = dict(
  scenarios=['A-2023-10-27', 'B-2023-10-27'],
  models=['Ensemble'],
  location='US',
  target='cumulative_hospitalization',
  age_group='0-130',
  uncertainty='None',
  zoom=None,
  annotations=None,
)


def visualization_editor(control_values=None, show_controls=True):
  controls = {**default_control_values, **(control_values or {})}

  init_scenarios = controls['scenarios']
  init_models = controls['models']
  init_location = controls['location']
  init_target = controls['target']
  init_age_group = controls['age_group']
  init_uncertainty = controls['uncertainty']
  init_zoom = controls['zoom']
  init_annotations = controls['annotations']

  figure_control_values = ChartControls(
    round_num=19,
    pathogen='covid',
    scenario_names=init_scenarios,
    model_names=init_models,
    location_name=init_location,
    age_group=init_age_group,
    target=init_target,
    certainty_percent=init_uncertainty,
    zoom=init_zoom,
    annotations=init_annotations,
  )
  chart = Chart(PlotType.LINE, figure_control_values)

  figure_container = html.Div(
    id='insight-visualization-figure',
    children=[chart.get_graph()],
    style={'height': '70vh'},
  )

  if not show_controls:
    return figure_container

  return dmc.Grid(
    children=[
      dmc.GridCol(
        [dcc.Store('chart-extent-store'), figure_container],
        id='visualization-column',
        span=dict(base=12, xl=8, lg=7, md=8),
      ),
      dmc.GridCol(
        dmc.Stack(
          [
            dmc.Card(
              dmc.Stack(
                [
                  scenarios_select(value=init_scenarios),
                  models_select(value=init_models),
                  location_select(value=init_location),
                  target_select(value=init_target),
                  age_group_select(value=init_age_group),
                  uncertainty_select(value=init_uncertainty),
                ],
                gap='sm',
              ),
              variant='soft',
            ),
            dmc.Card(
              zoom_control(value=init_zoom),
              variant='soft',
            ),
            dmc.Card(
              annotations_input(value=init_annotations),
              variant='soft',
            ),
          ],
          gap='md',
        ),
        id='controls-column',
        span=dict(base=12, xl=4, lg=5, md=4),
      ),
    ],
    mb=12,
  )


@callback(
  Output('insight-visualization-figure', 'children'),
  Input('scenarios-select', 'value'),
  Input('models-select', 'value'),
  Input('location-select', 'value'),
  Input('target-select', 'value'),
  Input('age-group-select', 'value'),
  Input('uncertainty-select', 'value'),
  Input('zoom-store', 'data'),
  Input('annotations-store', 'data'),
  # State('round-number-store', 'value'),
  prevent_initial_call=True,
)
def update_chart(
  scenario_names: list[str],
  model_names: list[str],
  location: str,
  target: str,
  age_group: str,
  uncertainty: str,
  zoom: dict[str, Any],
  annotations: list[dict[str, Any]] | None,
  # round_num: int,
):
  try:
    chart_controls = ChartControls(
      round_num=19,
      pathogen='covid',
      scenario_names=scenario_names,
      model_names=model_names,
      location_name=location,
      target=target,
      age_group=age_group,
      certainty_percent=uncertainty,
      zoom=zoom,
      annotations=annotations,
    )
    chart = Chart(PlotType.LINE, chart_controls)
    if not chart and not isinstance(chart, Chart):
      raise Exception('Chart not found or is not a valid chart')
    return [chart.get_graph()]  # must return a list here for the callback to work
  except Exception as e:
    print(f'Error creating chart: {e}')
    import traceback

    traceback.print_exc()
    return html.Div(f'Error loading chart: {str(e)}', style={'color': 'red'})


@callback(
  Output('chart-extent-store', 'data'),
  Input('graph', 'relayoutData'),
)
def sync_zoom_store(relayout):
  if not relayout:
    raise exceptions.PreventUpdate
  return dict(
    x={'min': relayout.get('xaxis.range[0]'), 'max': relayout.get('xaxis.range[1]')},
    y={'min': relayout.get('yaxis.range[0]'), 'max': relayout.get('yaxis.range[1]')},
  )


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
