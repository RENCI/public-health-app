from dash import callback, dcc, exceptions, html, Input, Output, State
import dash_mantine_components as dmc
from .controls.scenarios_select import scenarios_select
from .controls.location_select import location_select
from .controls.target_select import target_select
from .controls.age_group_select import age_group_select
from .controls.uncertainty_select import uncertainty_select
from .controls.ensemble_select import ensemble_select
from .controls.models_select import models_select
from .controls.zoom_control import zoom_control
from .controls.annotations_input import annotations_input
from src.components.chart import chart

available_rounds = [19]
current_round = 19

default_control_values = dict(
  scenarios=['77', '78', '79', '80', '81'],
  models=[],
  location='US',
  target='cumulative_hospitalization',
  age_group='0-130',
  uncertainty='None',
  ensemble='Ensemble',
  zoom={},
  annotations={},
)


def visualization_editor(control_values=None, show_controls=True):
  controls = {**default_control_values, **(control_values or {})}

  init_scenarios = controls['scenarios']
  init_models = controls['models']
  init_location = controls['location']
  init_target = controls['target']
  init_age_group = controls['age_group']
  init_uncertainty = controls['uncertainty']
  init_ensemble = controls['ensemble']
  init_zoom = controls['zoom']
  init_annotations = controls['annotations']

  figure_control_values = dict(
    scenarios=init_scenarios,
    models=init_models,
    location=init_location,
    target=init_target,
    age_group=init_age_group,
    uncertainty=init_uncertainty,
    ensemble=init_ensemble,
    zoom=init_zoom,
    annotations=init_annotations,
  )

  figure_container = html.Div(
    id='insight-visualization-figure',
    children=chart(control_values=figure_control_values),
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
                  ensemble_select(value=init_ensemble),
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
  prevent_initial_call=True,
)
def update_chart(scenarios, models, location, target, age_group, uncertainty, zoom, annotations):
  control_values = dict(
    scenarios=scenarios,
    models=models,
    location=location,
    target=target,
    age_group=age_group,
    uncertainty=uncertainty,
    zoom=zoom,
    annotations=annotations,
  )
  return chart(control_values=control_values)


@callback(
  Output('chart-extent-store', 'data'),
  Input('chart-figure', 'relayoutData'),
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
