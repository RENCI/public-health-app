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

from src.components.toolbar import toolbar
from src.components.save_insight_form import save_insight_form
from src.components.viz_editor import visualization_editor
from src.data.rounds.round19 import get_insight
from src.util.get_query_param import get_query_param

register_page(__name__, path_template='/explorer', name='Insight Explorer')

back_button = dmc.Anchor(
  dmc.Button(
    'Abandon Changes',
    leftSection=DashIconify(icon='feather:chevron-left'),
    variant='light',
    size='xs',
  ),
  id='back-button',
  href='/',
)

reset_button = dmc.Button(
  'Reset to Original',
  id='reset-button',
  leftSection=DashIconify(icon='feather:refresh-ccw'),
  variant='light',
  size='xs'
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
      visualization_editor(control_values=controls, show_controls=True),
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
