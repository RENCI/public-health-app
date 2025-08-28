from dash import callback, dcc, html, Input, no_update, Output, register_page, State
import dash_mantine_components as dmc
from urllib.parse import parse_qs
from dash_iconify import DashIconify
from src.data.round1 import get_insight, insights
from src.util.get_query_param import get_query_param

register_page(__name__, path_template='/viewer', name='Insight Details')

back_button = dmc.Anchor(
  '← Back to Insights',
  id='back-to-insights-button',
  href='/',
)
explorer_button = dcc.Link(
  dmc.Button(
    'Explore',
    leftSection=DashIconify(icon='feather:arrow-up-right'),
  ),
  id='explorer-button',
  href='#',
)
download_button = dcc.Link(
  dmc.Button(
    'Download',
    leftSection=DashIconify(icon='feather:download'),
    variant='outline',
  ),
  id='download-button',
  href='#',
)

toolbar = dmc.Flex(
  children=[
    back_button,
    dmc.Group([download_button, explorer_button])
  ],
  justify='space-between',
  align='center',
  mb=24,
)

layout = dmc.Container(
  [
    toolbar,
    dmc.Image(id='insight-view-image', radius='sm', style=dict(width='100%', height='auto', objectFit='cover')),
    dmc.Divider(my=24),
    dmc.Title(id='insight-view-title', order=1),
    dcc.Markdown(id='insight-view-description'),
  ],
  fluid=True
)

@callback(
  Output('insight-view-image', 'src'),
  Output('insight-view-title', 'children'),
  Output('insight-view-description', 'children'),
  Input('url', 'search'),
  State('custom-insights-store', 'data'),
)
def show_details(search, custom_insights):
  insight_id = get_query_param(search, 'id')
  item = get_insight(insight_id, custom_insights=custom_insights or [])
  if not item:
    return (
      'https://placehold.co/1200x400?text=Not found',
      'Insight not Found',
      '...',
    )
  return item['image_url'], item['title'], item['description']

@callback(
  Output('explorer-button', 'href'),
  Input('url', 'search')
)
def add_back_link_href(search):
  query = parse_qs(search.lstrip('?'))
  insight_id = query.get('id', [None])[0]
  return f'/explorer?starter={insight_id}'
