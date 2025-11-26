from typing import Any

import dash_mantine_components as dmc
from dash import (
  Input,
  Output,
  State,
  callback,
  exceptions,
  html,
  register_page,
)
from dash_iconify import DashIconify

from src.components.chart import DEFAULT_CONTROL_VALUES
from src.components.save_insight_form import save_insight_form
from src.components.toolbar import toolbar, toolbar_button
from src.components.viz_editor import visualization_editor
from src.data.rounds.round19 import get_insight
from src.util import get_query_param

register_page(__name__, path_template='/explorer', name='Insight Explorer')

back_button = dmc.Anchor(
  toolbar_button(
    'Abandon Changes',
    icon=DashIconify(icon='feather:chevron-left'),
  ),
  id='back-button',
  href='/',
)

reset_button = toolbar_button(
  'Reset to Original',
  icon=DashIconify(icon='feather:refresh-ccw'),
  id='reset-button',
)


insight_toolbar = toolbar(
  left=[back_button],
  right=[reset_button],
)


def insight_editor(insight_id, custom_insights=None):
  insight = get_insight(insight_id, custom_insights) or {}

  title = insight.get('title', '')
  description = insight.get('description', '')
  controls = insight.get('controls') or {}

  return html.Div(
    [
      visualization_editor(controls=controls, show_controls=True),
      save_insight_form(initial_title=title, initial_description=description),
    ],
    id='editor-contents',
  )


def layout(starter=None):
  return dmc.Container(
    [insight_toolbar, insight_editor(starter)],
    fluid=True,
    id='explorer-container',
  )


@callback(
  Output('back-button', 'href'),
  Input('url', 'search'),
)
def update_back_button_href(search):
  starter = get_query_param(search, 'starter')
  if not starter:
    raise exceptions.PreventUpdate
  return f'/insight/{starter}' if starter else '/'


@callback(
  Output('editor-contents', 'children'),
  Input('reset-button', 'n_clicks'),
  Input('url', 'search'),
  State('custom-insights-store', 'data'),
)
def render_or_reset_explorer(reset_clicks, search, custom_insights):
  starter_id = get_query_param(search, 'starter')

  return insight_editor(starter_id, custom_insights)


@callback(
  Output('chart-controls-store', 'data', allow_duplicate=True),
  Input('theme-store', 'data'),
  Input('scenarios-select', 'value'),
  Input('models-select', 'value'),
  Input('location-select', 'value'),
  Input('target-select', 'value'),
  Input('age-group-select', 'value'),
  Input('uncertainty-interval-select', 'value'),
  Input('annotations-store', 'data'),
  State('initial-page-load-chart-controls-store', 'data'),
  State('chart-controls-store', 'data'),
  State('url', 'pathname'),
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
  annotations: list[dict[str, Any]] | None,
  initial_chart_controls: dict[str, Any] | None,
  current_chart_controls: dict[str, Any] | None,
  pathname: str,
):
  if not pathname or not pathname.startswith('/explorer'):
    raise exceptions.PreventUpdate
  if not (scenario_ids and model_names and location_name and target and age_group):
    raise exceptions.PreventUpdate

  # saved_zoom comes from insight (stored in zoom field), current_zoom is the live state
  # We need to keep saved_zoom in the zoom field, and pass current_zoom separately
  new_chart_controls = dict(
    theme=theme,
    scenario_ids=[int(scenario_id) for scenario_id in scenario_ids],
    model_names=model_names,
    location_name=location_name,
    target=target,
    age_group=age_group,
    uncertainty_interval=uncertainty_interval,
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
