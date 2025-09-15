from dash import html, Input, Output, State, callback, exceptions, register_page
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from src.data.round19 import get_insight
from src.components.save_insight_form import save_insight_form
from src.components.viz_editor import visualization_editor
from src.util.get_query_param import get_query_param

register_page(__name__, path_template='/explorer', name='Insight Explorer')

back_button = dmc.Anchor('← Abandon Changes', href='/', id='back-button')

reset_button = dmc.Button(
  'Reset to Original',
  id='reset-button',
  leftSection=DashIconify(icon='feather:refresh-ccw'),
  variant='outline',
)

insight_toolbar = dmc.Flex(
  children=[back_button, dmc.Group([reset_button])],
  justify='space-between',
  align='center',
  mb=24,
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
  return f'/viewer?id={starter}' if starter else '/'

@callback(
  Output('editor-contents', 'children'),
  Input('reset-button', 'n_clicks'),
  Input('url', 'search'),
  State('custom-insights-store', 'data'),
)
def render_or_reset_explorer(reset_clicks, search, custom_insights):
  starter_id = get_query_param(search, 'starter')

  return insight_editor(starter_id, custom_insights)
