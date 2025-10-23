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

  init_plot_type: str = controls['plot_type']
  init_round_num: int = controls['round_num']
  init_scenarios: list[str] = controls['scenarios']
  init_models: list[str] = controls['models']
  init_location: str = controls['location']
  init_target: str = controls['target']
  init_age_group: str = controls['age_group']
  if 'x_start_date' in controls:
    init_x_start_date: str | None = controls['x_start_date']
  else:
    init_x_start_date = None
  init_x_axis: str = controls['x_axis']
  init_y_axis: str = controls['y_axis']
  init_certainty: str | None = controls['certainty']
  init_zoom: dict[str, dict[str, Any]] | None = controls['zoom']
  init_annotations: list[dict[str, Any]] | None = controls['annotations']

  figure_control_values = ChartControls(
    init_plot_type,
    init_round_num,
    init_scenarios,
    init_models,
    init_location,
    init_target,
    init_age_group,
    init_x_axis,
    init_y_axis,
    x_start_date=init_x_start_date,
    zoom=init_zoom,
    annotations=init_annotations,
    certainty_percent=init_certainty,
  )

  chart_controls_store = (
    dcc.Store(id='chart-controls-store', storage_type='local', data=figure_control_values),
  )

  # Get or create chart instance using the manager
  chart = chart_manager.get_chart(figure_control_values)

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
        [chart_controls_store, dcc.Store('chart-extent-store'), figure_container],
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
  Input('chart-controls-store', 'data'),
  # State('round-number-store', 'value'),
  prevent_initial_call=True,
)
def update_chart_figure(
  controls: dict[str, Any],
  # round_num: int,
):
  try:
    chart_controls = ChartControls(
      plot_type=controls['plot_type'],
      round_num=controls['round_num'],
      pathogen='covid',
      scenario_names=controls['scenarios'],
      model_names=controls['models'],
      location_name=controls['location'],
      target=controls['target'],
      age_group=controls['age_group'],
      x_axis=controls['x_axis'],
      y_axis=controls['y_axis'],
      x_start_date=controls['x_start_date'],
      certainty_percent=controls['certainty'],
      zoom=controls['zoom'],
      annotations=controls['annotations'],
    )

    # Get or create chart instance using the manager
    chart = chart_manager.get_chart(chart_controls)

    if not chart:
      raise Exception('Chart not found')
    return [chart.get_graph()]  # must return a list here for the callback to work
  except Exception as e:
    print(f'Error updating chart: {e}')
    import traceback

    traceback.print_exc()
    return html.Div(f'Error loading chart: {str(e)}', style={'color': 'red'})


@callback(
  Output('chart-controls-store', 'data'),
  Input('scenarios-select', 'value'),
  Input('models-select', 'value'),
  Input('location-select', 'value'),
  Input('target-select', 'value'),
  Input('age-group-select', 'value'),
  Input('certainty-select', 'value'),
  Input('zoom-store', 'value'),
  Input('annotations-store', 'value'),
  Input('graph', 'relayoutData'),
  State('chart-controls-store', 'data'),
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
    scenarios=scenarios,
    models=models,
    location=location,
    target=target,
    age_group=age_group,
    certainty=certainty,
    zoom=new_zoom,
    annotations=annotations,
  )
  return {**current_chart_controls, **new_chart_controls}


# TODO: Add this back in when we have a way to sync the zoom store with the chart controls store
# @callback(
#   Output('zoom-x-min', 'value'),
#   Output('zoom-x-max', 'value'),
#   Output('zoom-y-min', 'value'),
#   Output('zoom-y-max', 'value'),
#   Input('use-chart-zoom-button', 'n_clicks'),
#   State('chart-extent-store', 'data'),
#   prevent_initial_call=True,
# )
# def apply_current_zoom(n_clicks, current_zoom):
#   if not n_clicks or not current_zoom:
#     raise exceptions.PreventUpdate

#   return (
#     current_zoom['x'].get('min'),
#     current_zoom['x'].get('max'),
#     current_zoom['y'].get('min'),
#     current_zoom['y'].get('max'),
#   )
