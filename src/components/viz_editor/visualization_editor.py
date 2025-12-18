from typing import Any

import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import dcc, html

from dash_iconify import DashIconify

from src.components.chart import ChartControls
from src.components.chart.chart_instance_manager import ChartInstanceManager
from src.components.collapsible_card.collapsible_card import CollapsibleCard
from src.components.markdown_editor import markdown_editor
from src.components.insight_save_modal import insight_save_modal_button, insight_save_modal

from src.util.constants import (
  DEFAULT_CONTROL_VALUES,
  get_model_by_id,
  get_unique_model_names,
)

from .controls import (
  age_group_select,
  annotations_control,
  layout_select,
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
  init_chart_layout: str = controls['chart_layout']
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
    chart_layout=init_chart_layout,
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

  # get models with associated records available in the data
  df = chart.get_raw_dataframe()
  models_with_data = []
  if df is not None and not df.empty:
    model_ids_with_data = df['model_name'].unique().tolist()
    models_with_data = [
      get_model_by_id(model_id)['name'] for model_id in model_ids_with_data
    ]

  all_models = get_unique_model_names()
  model_options = [
    {'label': model, 'value': model, 'disabled': model not in models_with_data}
    for model in all_models
  ]

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
        [
          dmc.Tabs(
            [
              dmc.TabsList([
                dmc.TabsTab('Chart Controls', leftSection=DashIconify(icon='feather:sliders'), value='controls'),
                dmc.TabsTab('Save Insight', leftSection=DashIconify(icon='feather:save'), value='metadata'),
              ]),
              dmc.TabsPanel(
                dmc.Stack(
                  [
                    CollapsibleCard(
                      id={'index': 'insight-data-selection'},
                      title='Data Selection', 
                      children=dmc.Grid([
                        dmc.GridCol(scenarios_select(value=[str(scenario_id) for scenario_id in init_scenario_ids]), span=dict(base=12)),
                        dmc.GridCol(models_select(value=init_model_names, data=model_options), span=dict(base=12)),
                        dmc.GridCol(location_select(value=init_location_name), span=dict(base=12, sm=6)),
                        dmc.GridCol(target_select(value=init_target), span=dict(base=12, sm=6)),
                        dmc.GridCol(age_group_select(value=init_age_group), span=dict(base=12, sm=6)),
                        dmc.GridCol(uncertainty_interval_select(value=init_uncertainty_interval, disabled=init_plot_type == 'boxplot'), span=dict(base=12, sm=6)),
                      ]),
                    ).layout,
                    CollapsibleCard(
                      id={'index': 'insight-presentation'},
                      title='Presentation', 
                      children=dmc.Grid([
                        dmc.GridCol(layout_select(value=init_chart_layout), span=dict(base=12)),
                      ]),
                      initial_open=False,
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
                  ],
                  gap='md',
                ),
                py='sm',
                value='controls',
              ),
              dmc.TabsPanel(
                dmc.Stack(
                  [
                    dmc.Text(
                      'Additional information is required to save this custom insight. Please complete the fields below to proceed.',
                      size='sm',
                    ),
                    CollapsibleCard(
                      id={'index': 'insight-title'},
                      title='Title',
                      children=dmc.TextInput(
                        id='insight-title-input',
                        value='initial_title',
                        size='sm',
                        placeholder='Enter insight title',
                        inputProps=dict(className='insight-form-input'),
                        variant='filled',
                      ),
                      initial_open=True,
                    ).layout,
                    CollapsibleCard(
                      id={'index': 'insight-summary'},
                      title='Summary',
                      children=markdown_editor(
                        editor_id='insight-summary-input',
                        initial_value='initial_summary',
                      ),
                      initial_open=True,
                    ).layout,
                    CollapsibleCard(
                      id={'index': 'insight-discussion'},
                      title='Discussion',
                      children=markdown_editor(
                        editor_id='insight-discussion-input',
                        initial_value='initial_description',
                        min_height='300px',
                      ),
                      initial_open=True,
                    ).layout,
                    insight_save_modal_button(),
                    insight_save_modal(),
                  ],
                  gap='md',
                ),
                py='sm',
                value='metadata',
              ),
            ],
            value='controls',
            variant='default',
          ),
        ],
        id='controls-column',
        span=dict(base=12, xl=5),
      ),
    ],
    mb=12,
  )

from .callbacks import update_graph_figure, update_chart_controls, sync_zoom_store, apply_current_zoom
