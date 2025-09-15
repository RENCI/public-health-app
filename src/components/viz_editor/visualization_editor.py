from dash import callback, html, Input, Output
import dash_mantine_components as dmc
from .controls.scenarios_select import scenarios_select
from .controls.location_select import location_select
from .controls.target_select import target_select
from .controls.age_group_select import age_group_select
from .controls.uncertainty_select import uncertainty_select
from .controls.ensemble_select import ensemble_select
from .controls.models_select import models_select
from .controls.annotations_input import annotations_input
from src.components.chart import chart

available_rounds = [19]
current_round = 19

default_control_values = dict(
  scenarios=['1', '2', '3', '4', '5'],
  models=['18'],
  location='US',
  target='incident_hospitalization',
  age_group='0-130',
  uncertainty='None',
  ensemble='Ensemble',
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
  init_annotations = controls['annotations']

  figure_control_values = dict(
    scenarios=init_scenarios,
    models=init_models,
    location=init_location,
    target=init_target,
    age_group=init_age_group,
    uncertainty=init_uncertainty,
    ensemble=init_ensemble,
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
        figure_container,
        id='visualization-column',
        span=7,
      ),
      dmc.GridCol(
        dmc.Stack([
          dmc.Card(
            dmc.Grid(
              children=[
                dmc.GridCol(
                  scenarios_select(value=init_scenarios),
                  style=dict(padding='var(--mantine-spacing-sm)'),
                  span=dict(base=12),
                ),
                dmc.GridCol(
                  models_select(value=init_models),
                  style=dict(padding='var(--mantine-spacing-sm)'),
                  span=dict(base=12),
                ),
                dmc.GridCol(
                  location_select(value=init_location),
                  style=dict(padding='var(--mantine-spacing-sm)'),
                  span=12,
                ),
                dmc.GridCol(
                  target_select(value=init_target),
                  style=dict(padding='var(--mantine-spacing-sm)'),
                  span=12,
                ),
                dmc.GridCol(
                  age_group_select(value=init_age_group),
                  style=dict(padding='var(--mantine-spacing-sm)'),
                  span=dict(base=12),
                ),
                dmc.GridCol(
                  uncertainty_select(value=init_uncertainty),
                  style=dict(padding='var(--mantine-spacing-sm)'),
                  span=dict(base=12),
                ),
                dmc.GridCol(
                  ensemble_select(value=init_ensemble),
                  style=dict(padding='var(--mantine-spacing-sm)'),
                  span=dict(base=12),
                ),
              ],
              gutter=0,
            ),
            variant='soft',
          ),
          dmc.Card(
            dmc.Grid(
              children=[
                dmc.GridCol(
                  annotations_input(value=init_annotations),
                  style=dict(padding='var(--mantine-spacing-sm)'),
                  span=dict(base=12),
                ),
              ],
              gutter=0,
            ),
            variant='soft',
          ),
        ], gap='md'),
        id='controls-column',
        span=5,
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
  Input('annotations-store', 'data'),
  # prevent_initial_call=True,
)
def update_chart(scenarios, models, location, target, age_group, uncertainty, annotations):
  control_values = dict(
    scenarios=scenarios,
    models=models,
    location=location,
    target=target,
    age_group=age_group,
    uncertainty=uncertainty,
    annotations=annotations,
  )
  return chart(control_values=control_values)
