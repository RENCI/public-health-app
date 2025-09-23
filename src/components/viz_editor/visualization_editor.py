import dash_mantine_components as dmc
from dash import Input, Output, callback, html

from src.components.chart import Chart, ChartControls, PlotType

from .controls import (
  age_group_select,
  annotations_input,
  create_selector_grid_column,
  ensemble_select,
  location_select,
  models_select,
  scenarios_select,
  target_select,
  uncertainty_select,
)

available_rounds = [19]
current_round = 19

default_control_values = dict(
  scenarios=['1', '2'],
  models=['1', '2', '3'],
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

  figure_control_values = ChartControls(
    x_axis='date',
    y_axis='value',
    round_num=19,
    pathogen='covid',
    scenario_ids=init_scenarios,
    model_ids=init_models,
    location_name=init_location,
    age_group=init_age_group,
    target=init_target,
  )
  chart = Chart(PlotType.LINE, figure_control_values)

  figure_container = html.Div(
    id='insight-visualization-figure',
    children=chart.get_fig(),
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
        dmc.Stack(
          [
            dmc.Card(
              dmc.Grid(
                children=[
                  create_selector_grid_column(scenarios_select, init_scenarios),
                  create_selector_grid_column(models_select, init_models),
                  create_selector_grid_column(location_select, init_location),
                  create_selector_grid_column(target_select, init_target),
                  create_selector_grid_column(age_group_select, init_age_group),
                  create_selector_grid_column(uncertainty_select, init_uncertainty),
                  create_selector_grid_column(ensemble_select, init_ensemble),
                  create_selector_grid_column(annotations_input, init_annotations),
                ],
                gutter=0,
              ),
              variant='soft',
            ),
            dmc.Card(
              dmc.Grid(
                children=[
                  create_selector_grid_column(annotations_input, init_annotations),
                ],
                gutter=0,
              ),
              variant='soft',
            ),
          ],
          gap='md',
        ),
        id='controls-column',
        span=5,
      ),
    ],
    mb=12,
  )


@callback(
  Output('insight-visualization-figure', 'children'),
  Input('chart-type-select', 'value'),
  Input('scenarios-select', 'value'),
  Input('models-select', 'value'),
  Input('location-select', 'value'),
  Input('target-select', 'value'),
  Input('age-group-select', 'value'),
  Input('uncertainty-select', 'value'),
  Input('annotations-store', 'data'),
  # prevent_initial_call=True,
)
def update_chart(
  chart_type: str,
  scenario_ids: list[int],
  models,
  location,
  target,
  age_group,
  uncertainty,
  annotations,
):
  chart_controls = ChartControls(
    x_axis='date',
    y_axis='value',
    round_num=19,
    pathogen='covid',
    scenario_ids=scenario_ids,
    model_ids=models,
    location_name=location,
    target=target,
    age_group=age_group,
    certainty_percent=uncertainty,
    annotations=annotations,
  )
  return Chart(PlotType(chart_type), chart_controls)
