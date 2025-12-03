import copy
from typing import Any

import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import Input, Output, State, callback, dcc, exceptions, html

from src.components.chart import (
  DEFAULT_CONTROL_VALUES,
  Chart,
  ChartControls,
  ChartInstanceManager,
  Zoom,
)

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

  # Initial values for controls

  init_theme: str = controls.get('theme', 'light')
  init_plot_type: str = controls['plot_type']
  init_round_num: int = controls['round_num']
  init_scenario_ids: list[int] = controls['scenario_ids']
  init_scenario_variables: list[dict] = controls['scenario_variables']
  init_model_names: list[str] = controls['model_names']
  init_location_name: str = controls['location_name']
  init_target: str = controls['target']
  init_age_group: str = controls['age_group']
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
    zoom=init_zoom,
    annotations=init_annotations,
    uncertainty_interval=init_uncertainty_interval,
  )

  # Stores

  # saved_zoom_store is in memory and gets initialized from controls (insight saved_zoom)
  saved_zoom_store = dcc.Store(
    id='saved-zoom-store',
    data=copy.deepcopy(init_zoom) if init_zoom else None,
    storage_type='session',
  )

  chart_controls_store = dcc.Store(
    id='chart-controls-store',
    storage_type='local',
    data=DEFAULT_CONTROL_VALUES,
  )
  chart_loading_store = dcc.Store(id='chart-loading-store', data=False)

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
  graph = dcc.Graph(id='graph', figure=figure)

  if saved_zoom_store.data is None:
    saved_zoom_store.data = (
      chart.controls.saved_zoom.to_dict() if chart.controls.saved_zoom else None
    )

  if not chart:
    return html.Div(
      id='insight-visualization-figure',
      children=[
        chart_loading_store,
        html.Div(
          [
            html.Div(
              graph,
              id='chart-wrapper',
              style={'opacity': '1', 'transition': 'opacity 0.2s'},
            ),
            html.Div(
              dmc.Center(
                dmc.Loader(size='lg', variant='bars'),
                style={'minHeight': '400px', 'width': '100%'},
              ),
              id='chart-loading-spinner',
              style={
                'display': 'none',
                'position': 'absolute',
                'top': '0',
                'left': '0',
                'right': '0',
                'bottom': '0',
                'zIndex': '1000',
                'backgroundColor': 'rgba(255, 255, 255, 0.8)',
              },
            ),
          ],
          id='chart-container',
          style={'position': 'relative'},
        ),
      ],
      style={'min-height': '45vh'},
    )

  # Insight page (no controls)
  if not show_controls:
    return html.Div(
      [
        saved_zoom_store,
        chart_controls_store,
        initial_page_load_chart_controls_store,
        chart_loading_store,
        html.Div(
          [
            html.Div(
              graph,
              id='chart-wrapper',
              style={'opacity': '1', 'transition': 'opacity 0.2s'},
            ),
            html.Div(
              dmc.Center(
                dmc.Loader(size='lg', variant='bars'),
                style={'minHeight': '400px', 'width': '100%'},
              ),
              id='chart-loading-spinner',
              style={
                'display': 'none',
                'position': 'absolute',
                'top': '0',
                'left': '0',
                'right': '0',
                'bottom': '0',
                'zIndex': '1000',
                'backgroundColor': 'rgba(255, 255, 255, 0.8)',
              },
            ),
          ],
          id='chart-container',
          style={'position': 'relative'},
        ),
      ],
    )

  # Explorer page (with controls)
  return dmc.Grid(
    [
      dmc.GridCol(
        [
          saved_zoom_store,
          chart_controls_store,
          initial_page_load_chart_controls_store,
          chart_loading_store,
          html.Div(
            [
              html.Div(
                graph,
                id='chart-wrapper',
                style={'opacity': '1', 'transition': 'opacity 0.2s'},
              ),
              html.Div(
                dmc.Center(
                  dmc.Loader(size='lg', variant='bars'),
                  style={'minHeight': '400px', 'width': '100%'},
                ),
                id='chart-loading-spinner',
                style={
                  'display': 'none',
                  'position': 'absolute',
                  'top': '0',
                  'left': '0',
                  'right': '0',
                  'bottom': '0',
                  'zIndex': '1000',
                  'backgroundColor': 'rgba(255, 255, 255, 0.8)',
                },
              ),
            ],
            id='chart-container',
            style={'position': 'relative'},
          ),
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
  Output('chart-loading-store', 'data'),
  Input('chart-controls-store', 'data'),
  prevent_initial_call=True,
)
def set_chart_loading(current_chart_controls: dict[str, Any] | None):
  """Set loading state to True when chart controls change."""
  if not current_chart_controls:
    raise exceptions.PreventUpdate
  return True


@callback(
  Output('graph', 'figure'),
  Output('chart-loading-store', 'data', allow_duplicate=True),
  Input('chart-controls-store', 'data'),
  State('graph', 'relayoutData'),
  prevent_initial_call=True,
)
def update_fig_with_new_controls(
  current_chart_controls: dict[str, Any],
  relayout_data: dict[str, Any] | None,
):
  if not current_chart_controls:
    raise exceptions.PreventUpdate

  # Calculate current zoom from relayoutData if available
  current_zoom = (
    Chart.calculate_zoom_from_relayout(relayout_data) if relayout_data is not None else None
  )

  try:
    chart_controls = ChartControls.from_dict(current_chart_controls)

    # Get or create chart instance using the manager (cached without current_zoom)
    chart = chart_manager.get_chart(chart_controls, current_zoom=current_zoom)

    if not chart:
      raise Exception('Chart not found')

    figure = chart.get_fig()
    # Set loading to False when figure is ready
    return figure, False
  except Exception as e:
    import traceback

    print(traceback.print_exception(e))
    error_figure = go.Figure(layout=go.Layout(title='Error loading chart'))
    return error_figure, False


@callback(
  Output('chart-controls-store', 'data', allow_duplicate=True),
  Input('saved-zoom-store', 'data'),
  State('chart-controls-store', 'data'),
  prevent_initial_call=True,
)
def update_chart_controls_with_zoom(
  saved_zoom_data: dict[str, dict[str, Any]] | None,
  current_chart_controls: dict[str, Any] | None,
):
  if not current_chart_controls:
    raise exceptions.PreventUpdate
  saved_zoom = Zoom.from_dict(saved_zoom_data)
  if saved_zoom is not None:
    current_chart_controls['saved_zoom'] = saved_zoom.to_dict()
  return current_chart_controls


@callback(
  Output('chart-loading-spinner', 'style'),
  Output('chart-wrapper', 'style'),
  Input('chart-loading-store', 'data'),
)
def update_chart_loading_display(is_loading: bool):
  """Show/hide loading spinner overlay and adjust chart opacity based on loading state."""
  if is_loading:
    return (
      {
        'display': 'block',
        'position': 'absolute',
        'top': '0',
        'left': '0',
        'right': '0',
        'bottom': '0',
        'zIndex': '1000',
        'backgroundColor': 'rgba(255, 255, 255, 0.8)',
      },
      {'opacity': '0.5', 'transition': 'opacity 0.2s'},
    )
  else:
    return (
      {
        'display': 'none',
        'position': 'absolute',
        'top': '0',
        'left': '0',
        'right': '0',
        'bottom': '0',
        'zIndex': '1000',
        'backgroundColor': 'rgba(255, 255, 255, 0.8)',
      },
      {'opacity': '1', 'transition': 'opacity 0.2s'},
    )
