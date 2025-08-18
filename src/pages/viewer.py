from dash import callback, dcc, html, Input, no_update, Output, register_page
import dash_mantine_components as dmc
from urllib.parse import parse_qs
from dash_iconify import DashIconify
from src.data.insights import insights

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
    'Download Insight',
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
)

layout = dmc.Container(
  [
    toolbar,
    dmc.Space(h=48),
    dmc.Image(id='insight-view-image', radius='sm', style=dict(width='100%', height='auto', objectFit='cover')),
    dmc.Divider(my=24),
    dcc.Markdown(id='insight-view-details'),
  ],
  fluid=True
)

@callback(
  Output('insight-view-image', 'src'),
  Output('insight-view-details', 'children'),
  Input('url', 'search'),
)
def show_details(search):
  query = parse_qs(search.lstrip('?'))
  insight_id = query.get('id', [None])[0]
  item = next((x for x in insights if x['id'] == insight_id), None)
  if not item:
    return 'https://placehold.co/1200x400?text=Not found', f'## Insight not found'
  return item['image_url'], item['details']

# @callback(
#   Output('back-to-insights-button', 'href'),
#   Input('url', 'search'),
# )
# def update_back_button_href(search):
#   query = parse_qs(search.lstrip('?'))
#   insight_id = query.get('id', [None])[0]
#   return f'/viewer?id={insight_id}' if insight_id else '/'

@callback(
  Output('explorer-button', 'href'),
  Input('url', 'search')
)
def add_back_link_href(search):
  query = parse_qs(search.lstrip('?'))
  insight_id = query.get('id', [None])[0]
  return f'/explorer?starter={insight_id}'
