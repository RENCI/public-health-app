import yaml
from typing import Any

import dash_mantine_components as dmc
from dash import Input, Output, State, callback, dcc, exceptions, html

from src.components.chart import ChartControls, PlotType
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
  scenarios=['A-2023-10-27', 'B-2023-10-27'],
  models=['Ensemble'],
  location='US',
  target='cumulative_hospitalization',
  age_group='0-130',
  certainty='None',
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
  init_certainty = controls['certainty']
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
    certainty_percent=init_certainty,
    zoom=init_zoom,
    annotations=init_annotations,
  )

  # Get or create chart instance using the manager
  chart = chart_manager.get_chart(figure_control_values, PlotType.LINE)

  figure_container = html.Div(
    id='insight-visualization-figure',
    children=[chart.get_graph()],
    style={'min-height': '45vh'},
  )

  if not show_controls:
    return figure_container

  return dmc.Grid(
    children=[
      dmc.GridCol(
        [dcc.Store('chart-extent-store'), figure_container],
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
                  dmc.GridCol(scenarios_select(value=init_scenarios), span=dict(base=12)),
                  dmc.GridCol(models_select(value=init_models), span=dict(base=12)),
                  dmc.GridCol(location_select(value=init_location), span=dict(base=12, sm=6)),
                  dmc.GridCol(target_select(value=init_target), span=dict(base=12, sm=6)),
                  dmc.GridCol(age_group_select(value=init_age_group), span=dict(base=12, sm=6)),
                  dmc.GridCol(certainty_select(value=init_certainty), span=dict(base=12, sm=6)),
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
  Output('insight-visualization-figure', 'children'),
  Input('scenarios-select', 'value'),
  Input('models-select', 'value'),
  Input('location-select', 'value'),
  Input('target-select', 'value'),
  Input('age-group-select', 'value'),
  Input('certainty-select', 'value'),
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
  certainty: str,
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
      certainty_percent=certainty,
      zoom=zoom,
      annotations=annotations,
    )

    # Get or create chart instance using the manager
    chart = chart_manager.get_chart(chart_controls, PlotType.LINE)

    if not chart:
      raise Exception('Chart not found')
    return [chart.get_graph()]  # must return a list here for the callback to work
  except Exception as e:
    print(f'Error updating chart: {e}')
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
