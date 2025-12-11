from typing import Any

import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import Input, Output, State, callback, dcc, exceptions, html

from dash_iconify import DashIconify

from src.components.chart import ChartControls
from src.components.chart.chart_instance_manager import ChartInstanceManager
from src.components.collapsible_card.collapsible_card import CollapsibleCard
from src.components.markdown_editor import markdown_editor
from src.util.constants import DEFAULT_CONTROL_VALUES

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


def visualization_editor(controls=None, show_controls=True):
  if not controls:
    controls = DEFAULT_CONTROL_VALUES
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
    data=DEFAULT_CONTROL_VALUES,
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

  controls_dict = {**DEFAULT_CONTROL_VALUES, **figure_control_values}
  chart_controls = ChartControls.from_dict(controls_dict)
  chart = chart_manager.get_chart(chart_controls)
  figure = chart.get_fig() if chart else go.Figure()
  graph = dcc.Graph(id='graph', figure=figure, 
                    config={'modeBarButtonsToRemove': ['toImage', 'pan2d', 'lasso2d', 'select2d', 'autoScale2d'], 'displaylogo': False},)

  if not chart:
    return html.Div(
      id='insight-visualization-figure',
      children=graph,
      style={'min-height': '45vh'},
    )

  if not show_controls:
    return graph

  return dmc.Grid(
    [
      dmc.GridCol(
        [
          chart_controls_store,
          initial_page_load_chart_controls_store,
          chart_extent_store,
          graph,
        ],
        id='visualization-column',
        span=dict(base=12, xl=7),
        style={'display': 'flex', 'flexDirection': 'column'},
      ),
      dmc.GridCol(
        dmc.Stack(
          [
            CollapsibleCard(
              id={'index': 'insight-title'},
              title='Title',
              children=dmc.TextInput(
                id='insight-title-input',
                value='initial_title',
                size='lg',
                placeholder='Enter insight title',
                inputProps=dict(className='insight-form-input'),
                variant='filled',
              ),
              initial_open=False,
            ).layout,
            CollapsibleCard(
              id={'index': 'insight-summary'},
              title='Summary',
              children=markdown_editor(
                editor_id='insight-summary-input',
                initial_value='initial_summary',
              ),
              initial_open=False,
            ).layout,
            CollapsibleCard(
              id={'index': 'insight-data-selection'},
              title='Data Selection', 
              children=dmc.Grid(
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
            ).layout,
            #dmc.Card(
            #  zoom_control(value=init_zoom),
            #  variant='soft',
            #  style={'display': 'none'} if init_plot_type == 'boxplot' else {},
            #),
            # Remove zoom control for now, but render the Store to keep things in sync
            dcc.Store(id='zoom-store', data=init_zoom),
            CollapsibleCard(
              id={'index': 'insight-annotations'},
              title='Annotations',
              children=annotations_control(value=init_annotations),
              style={'display': 'none'} if init_plot_type == 'boxplot' else {},
            ).layout,
            CollapsibleCard(
              id={'index': 'insight-discussion'},
              title='Discussion',
              children=markdown_editor(
                editor_id='insight-discussion-input',
                initial_value='initial_description',
                min_height='300px',
              ),
              initial_open=False,
            ).layout,
          ],
          gap='md',
        ),
        id='controls-column',
        span=dict(base=12, xl=5),
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
