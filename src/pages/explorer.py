from dash import callback, ctx, dcc, exceptions, html, Input, no_update, Output, register_page, State
import dash_mantine_components as dmc
from urllib.parse import parse_qs
from dash_iconify import DashIconify
from src.data.insights import get_insight
from src.data.templates import templates
from src.components.save_insight_form import save_insight_form
from src.components.viz_editor import visualization_editor
from src.util.get_query_param import get_query_param

register_page(__name__, path_template='/explorer', name='Insight Explorer')

back_button = dmc.Anchor('← Abandon Changes', href='/', id='back-button')

reset_button = dcc.Link(
  dmc.Button(
    'Reset to Original',
    leftSection=DashIconify(icon='feather:refresh-ccw'),
    variant='outline',
  ),
  id='reset-button',
  href='#',
)

toolbar = dmc.Flex(
  children=[
    back_button,
    dmc.Group([reset_button])
  ],
  justify='space-between',
  align='center',
  mb=24,
)

def layout(starter=None, custom_insights=None):
  insight = get_insight(starter, custom_insights) or {}
  controls = insight.get('controls') or {}
  return dmc.Container(
    [
      toolbar,
      visualization_editor(controls),
      save_insight_form(
        initial_title=insight.get('title', ''),
        initial_description=insight.get('description', ''),
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
  return f'/viewer?id={starter}' if starter else '/'

@callback(
  Output('explorer-container', 'children'),
  Input('url', 'search'),
  State('custom-insights-store', 'data'),
)
def render_explorer(search, custom_insights):
  starter = get_query_param(search, 'starter')
  return layout(starter, custom_insights)