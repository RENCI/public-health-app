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
from src.util import all_not_none, get_query_param

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


def insight_editor(insight_id, custom_insights=None) -> html.Div:
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
def update_back_button_href(search: str) -> str:
  starter = get_query_param(search, 'starter')
  if not starter:
    raise exceptions.PreventUpdate
  return f'/insight/{starter}' if starter else '/'


# @callback(
#   Output('editor-contents', 'children'),
#   Output('chart-controls-store', 'data', allow_duplicate=True),
#   Input('reset-button', 'n_clicks'),
#   Input('url', 'search'),
#   State('custom-insights-store', 'data'),
#   prevent_initial_call=True,
# )
# def render_or_reset_explorer(
#   reset_clicks: int,
#   search: str | None,
#   custom_insights: list[dict[str, Any]],
# ) -> tuple[html.Div, dict[str, Any]]:
#   starter_id = get_query_param(search, 'starter')

#   return (
#     insight_editor(starter_id, custom_insights),
#     DEFAULT_CONTROL_VALUES,
#   )


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
  current_chart_controls: dict[str, Any] | None,
  pathname: str,
) -> dict[str, Any]:
  if not pathname or not pathname.startswith('/explorer'):
    print('Could not update chart controls: not on explorer page')
    raise exceptions.PreventUpdate
  if not all_not_none(scenario_ids, model_names, location_name, target, age_group):
    print('Could not update chart controls: not all required parameters are present')
    raise exceptions.PreventUpdate

  # saved_zoom comes from insight, current_zoom is the live state
  # we need to keep saved_zoom in the saved_zoom field, and pass current_zoom separately
  new_chart_controls = {
    **(current_chart_controls or {}),
    'theme': theme,
    'scenario_ids': [int(scenario_id) for scenario_id in scenario_ids],
    'model_names': model_names,
    'location_name': location_name,
    'target': target,
    'age_group': age_group,
    'uncertainty_interval': uncertainty_interval,
    'annotations': annotations,
  }
  return new_chart_controls
