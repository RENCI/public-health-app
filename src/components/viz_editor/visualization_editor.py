from typing import Any

import dash_mantine_components as dmc
from dash import Input, Output, callback, dcc, html

from src.components.chart import Chart, ChartControls, PlotType

from .controls import (
  age_group_select,
  annotations_input,
  create_selector_grid_column,
  location_select,
  models_select,
  scenarios_select,
  target_select,
  uncertainty_select,
)

available_rounds = [19]
current_round = 19

default_control_values = dict(
  scenarios=['A-2023-10-27', 'B-2023-10-27'],
  models=['Ensemble_LOP'],
  location='US',
  target='incident_hospitalization',
  age_group='0-130',
  uncertainty='None',
  annotations={},
)


def visualization_editor(control_values=None, show_controls=True):
  controls = {**default_control_values, **(control_values or {})}

  init_scenarios: list[str] = controls.get('scenarios', ['A-2023-10-27', 'B-2023-10-27'])
  init_models: list[str] = controls.get('models', ['Ensemble_LOP'])
  init_location: str = controls.get('location', 'US')
  init_target: str = controls.get('target', 'incident_hospitalization')
  init_age_group: str = controls.get('age_group', '0-130')
  init_uncertainty: str | None = controls.get('uncertainty')
  init_annotations: dict[str, Any] = controls.get('annotations', {})
  x_axis: str = controls.get('x_axis', 'date')
  y_axis: str = controls.get('y_axis', 'value')
  round_num: int = controls.get('round_num', 19)

  figure_control_values = ChartControls(
    x_axis=x_axis,
    y_axis=y_axis,
    round_num=round_num,
    pathogen='covid',
    scenario_ids=init_scenarios,
    model_ids=init_models,
    location_name=init_location,
    age_group=init_age_group,
    target=init_target,
    certainty_percent=init_uncertainty,
    annotations=init_annotations,
  )
  chart = Chart(PlotType.LINE, figure_control_values)

  figure_container = html.Div(
    id='insight-visualization-figure',
    children=dcc.Graph(figure=chart.get_fig()),
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
                  # create_selector_grid_column(ensemble_select, init_ensemble),
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
  chart = Chart(PlotType(PlotType.LINE), chart_controls)
  return dcc.Graph(figure=chart.get_fig())
