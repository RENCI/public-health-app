from dash import callback, dcc, html, Input, no_update, Output, register_page
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from src.data.insights import insights

register_page(__name__, path_template='/viewer/<insight_id>', name='Insight Details')

back_button = dmc.Anchor(
  '← Back to Insights',
  id='back-to-insights-button',
  href='/',
)
editor_button = dcc.Link(
  dmc.Button(
    'Open in Insight Editor',
    leftSection=DashIconify(icon='feather:edit-3'),
  ),
  id='editor-button',
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
    dmc.Group([download_button, editor_button])
  ],
  justify='space-between',
  align='center',
)

layout = dmc.Container(
  [
    toolbar,
    dmc.Space(h=48),
    dmc.Image(id='detail-image', radius='sm', style=dict(width='100%', height='auto', objectFit='cover')),
    dmc.Divider(my=24),
    dcc.Markdown(id='detail-details'),
  ],
  fluid=True
)

@callback(
  Output('detail-image', 'src'),
  Output('detail-details', 'children'),
  Input('url', 'pathname'),
)
def show_details(pathname):
  insight_id = pathname.split('/')[-1]
  item = next((x for x in insights if x['id'] == insight_id), None)
  if not item:
    return '', ''
  return item['image_url'], item['details']

@callback(
  Output('editor-button', 'href'),
  Input('url', 'pathname')
)
def add_back_link_href(pathname):
  insight_id = pathname.split('/')[-1]
  return f'/editor/{insight_id}'
