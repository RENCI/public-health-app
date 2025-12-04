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

from src.components.toolbar import toolbar, toolbar_button
from src.components.insight_save_modal import insight_save_modal_button, insight_save_modal
from src.components.toolbar import toolbar
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
  right=[reset_button, insight_save_modal_button()],
)


def insight_editor(insight_id, custom_insights=None):
  insight = get_insight(insight_id, custom_insights) or {}

  title = insight.get('title', '')
  description = insight.get('description', '')
  controls = insight.get('controls') or {}

  return html.Div(
    visualization_editor(controls=controls, show_controls=True),
    id='editor-contents',
  )


def layout(starter=None):
  insight = get_insight(starter) or {}

  title = insight.get('title', '')
  summary = insight.get('summary', '')
  description = insight.get('description', '')

  return dmc.Container(
    [
      insight_toolbar,
      insight_editor(starter),
      insight_save_modal(
        initial_title=title,
        initial_summary=summary,
        initial_description=description,
      ),
    ],
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
  Output('insight-title-input', 'value'),
  Output({'type': 'editor', 'id': 'insight-description-input'}, 'value'),
  Input('url', 'search'),
  State('custom-insights-store', 'data'),
)
def update_modal_initial_values(search, custom_insights):
  starter_id = get_query_param(search, 'starter')
  insight = get_insight(starter_id, custom_insights) or {}
  title = insight.get('title', '')
  description = insight.get('description', '')
  return title, description
