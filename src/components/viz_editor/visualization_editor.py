from typing import Any

import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import Input, Output, State, callback, dcc, exceptions, html

from src.components.chart import ChartControls
from src.components.chart.chart_instance_manager import ChartInstanceManager

from .controls import (
  age_group_select,
  annotations_control,
  location_select,
  models_select,
  scenarios_select,
  target_select,
  uncertainty_interval_select,
  zoom_control,
)

# Global instance of the chart manager
chart_manager = ChartInstanceManager()


default_control_values = dict(
  theme='light',
  plot_type='line',
  round_num=19,
  scenario_ids=[77, 78],
  scenario_variables=[
    {
      'name': 'Vaccination Strategy',
      'options': ['High risk', 'All ages'],
      'selected_option': 'All ages',
    }
  ],
  model_names=['Ensemble'],
  location_name='US',
  target='incident_hospitalization',
  x_axis='target_end_date',
  y_axis='value',
  x_start_date='2025-01-01',
  age_group='0-130',
  uncertainty_interval='95%',
  annotations=None,
  zoom=None,
)


def visualization_editor(controls=None, show_controls=True):
  if not controls:
    controls = default_control_values
    print('No controls provided, using default values')

  init_theme: str = controls.get('theme', 'light')
  init_plot_type: str = controls['plot_type']
  init_round_num: int = controls['round_num']
  init_scenario_ids: list[int] = controls['scenario_ids']
  init_scenario_variables: list[dict] = controls['scenario_variables']
  init_model_names: list[str] = controls['model_names']
  init_location_name: str = controls['location_name']
  init_target: str = controls['target']
  init_age_group: str = controls['age_group']
  init_x_start_date: str | None = controls.get('x_start_date', None)
  init_x_axis: str = controls.get('x_axis', None)
  init_y_axis: str = controls.get('y_axis', None)
  init_uncertainty_interval: str | None = controls.get('uncertainty_interval', None)
  init_zoom: dict[str, dict[str, Any]] | None = controls.get('zoom', None)
  init_annotations: list[dict[str, Any]] | None = controls.get('annotations', None)

  figure_control_values = dict(
    theme=init_theme,
    plot_type=init_plot_type,
    round_num=init_round_num,
    scenario_ids=init_scenario_ids,
    scenario_variables=init_scenario_variables,
    model_names=init_model_names,
    location_name=init_location_name,
    target=init_target,
    age_group=init_age_group,
    x_axis=init_x_axis,
    y_axis=init_y_axis,
    x_start_date=init_x_start_date,
    zoom=init_zoom,
    annotations=init_annotations,
    uncertainty_interval=init_uncertainty_interval,
  )

  chart_extent_store = dcc.Store(id='chart-extent-store', storage_type='local')
  chart_controls_store = dcc.Store(
    id='chart-controls-store',
    storage_type='local',
    data=default_control_values,
  )

  # This is kind of a hack used to update the chart-controls-store when the page is loaded
  # for the first time. This is necessary because the callback that updates the
  # chart-controls-store is not called when the page is initially loaded so it needs to be
  # triggered, and since the chart-controls-store is stored in local storage it will preserve
  # its values (potentially from a different chart type on a different insight) when the page
  # is reloaded unless it's reset.
  initial_page_load_chart_controls_store = dcc.Store(
    id='initial-page-load-chart-controls-store',
    storage_type='memory',
    data=figure_control_values,
  )

  controls_dict = {**default_control_values, **figure_control_values}
  chart_controls = ChartControls.from_dict(controls_dict)
  chart = chart_manager.get_chart(chart_controls)
  figure = chart.get_fig() if chart else go.Figure()
  graph = dcc.Graph(id='graph', figure=figure)
  caption = dmc.Text(id='caption', children=chart.build_caption(), style=dict(fontStyle='italic'), mt='md', size='sm', c='grey')

  if not chart:
    return html.Div(
      id='insight-visualization-figure',
      children=graph,
      style={'min-height': '45vh'},
    )

  if not show_controls:
    return [graph, caption]

  return dmc.Grid(
    [
      dmc.GridCol(
        [
          chart_controls_store,
          initial_page_load_chart_controls_store,
          chart_extent_store,
          graph,
          caption,
        ],
        id='visualization-column',
        span=dict(base=12, xl=8, lg=7),
        style={'display': 'flex', 'flexDirection': 'column'},
      ),
      dmc.GridCol(
        dmc.Stack(
          [
            dmc.Card(
              dmc.Grid(
                [
                  dmc.GridCol(
                    scenarios_select(value=[str(scenario_id) for scenario_id in init_scenario_ids]),
                    span=dict(base=12),
                  ),
                  dmc.GridCol(
                    models_select(value=init_model_names, disabled=init_plot_type == 'boxplot'),
                    span=dict(base=12),
                  ),
                  dmc.GridCol(location_select(value=init_location_name), span=dict(base=12, sm=6)),
                  dmc.GridCol(target_select(value=init_target), span=dict(base=12, sm=6)),
                  dmc.GridCol(age_group_select(value=init_age_group), span=dict(base=12, sm=6)),
                  dmc.GridCol(
                    uncertainty_interval_select(
                      value=init_uncertainty_interval, disabled=init_plot_type == 'boxplot'
                    ),
                    span=dict(base=12, sm=6),
                  ),
                ],
              ),
              variant='soft',
            ),
            dmc.Card(
              zoom_control(value=init_zoom),
              variant='soft',
              style={'display': 'none'} if init_plot_type == 'boxplot' else {},
            ),
            dmc.Card(
              annotations_control(value=init_annotations),
              variant='soft',
              style={'display': 'none'} if init_plot_type == 'boxplot' else {},
            ),
          ],
          gap='md',
        ),
        id='controls-column',
        span=dict(base=12, xl=4, lg=5),
      ),
    ],
    mb=12,
  )


@callback(
  Output('graph', 'figure'),
  Output('caption', 'children'),
  Input('chart-controls-store', 'data'),
  # prevent_initial_call=True,
)
def update_graph_figure(
  current_chart_controls: dict[str, Any],
):
  if not current_chart_controls:
    raise exceptions.PreventUpdate

  try:
    chart_controls = ChartControls.from_dict({**default_control_values, **current_chart_controls})

    # Get or create chart instance using the manager
    chart = chart_manager.get_chart(chart_controls)

    if not chart:
      raise Exception('Chart not found')

    return chart.get_fig(), chart.build_caption()
  except Exception as e:
    import traceback

    print(traceback.print_exception(e))
    return go.Figure(layout=go.Layout(title='Error loading chart'))


@callback(
  Output('chart-controls-store', 'data', allow_duplicate=True),
  Input('theme-store', 'data'),
  Input('scenarios-select', 'value'),
  Input('models-select', 'value'),
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

  if relayout and 'xaxis.range' in relayout and 'yaxis.range' in relayout:
    new_zoom = {
      'x': {
        'min': relayout.get('xaxis.range[0]'),
        'max': relayout.get('xaxis.range[1]'),
      },
      'y': {
        'min': relayout.get('yaxis.range[0]'),
        'max': relayout.get('yaxis.range[1]'),
      },
    }
  else:
    new_zoom = None

  new_chart_controls = dict(
    theme=theme,
    scenario_ids=[int(scenario_id) for scenario_id in scenario_ids],
    model_names=model_names,
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
    **default_control_values,
    **current_chart_controls,
    **initial_chart_controls,
    **new_chart_controls,
  }


@callback(
  Output('chart-controls-store', 'data', allow_duplicate=True),
  Input('round-select', 'value'),
  prevent_initial_call=True,
)
def update_chart_controls_for_round(round_number: str):
  if not round_number:
    raise exceptions.PreventUpdate
  return default_control_values | {
    'round_num': int(round_number),
  }


@callback(
  Output('chart-extent-store', 'data'),
  Input('graph', 'relayoutData'),
)
def sync_zoom_store(relayout):
  if not relayout:
    raise exceptions.PreventUpdate
  if 'xaxis.range[0]' in relayout and 'yaxis.range[0]' in relayout:
    return {
      'x': {
        'min': relayout.get('xaxis.range[0]'),
        'max': relayout.get('xaxis.range[1]'),
      },
      'y': {
        'min': relayout.get('yaxis.range[0]'),
        'max': relayout.get('yaxis.range[1]'),
      },
    }
  else:
    return None


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
