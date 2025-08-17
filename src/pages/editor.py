from dash import callback, ctx, dcc, html, Input, no_update, Output, register_page, State
import dash_mantine_components as dmc
from urllib.parse import parse_qs
from dash_iconify import DashIconify
from src.data.insights import insights
from src.data.templates import templates
from src.components.markdown_editor import markdown_editor
from src.components.editor import save_form, visualization_editor

register_page(__name__, path_template='/editor', name='Insight Editor')

back_button = dmc.Anchor('← Abandon Changes', href='/', id='back-button')

reset_button = dcc.Link(
  dmc.Button(
    'Reset',
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
)

layout = dmc.Container(
  [
    toolbar,
    dmc.Title('Insight Editor', id='insight-editor-title', order=1, mt=24),
    visualization_editor,
    dmc.Space(h=24),
    markdown_editor(
      label='Insight Details',
      editor_id='insight-details',
      preview_id='insight-preview',
    ),
    save_form,
  ],
  fluid=True,
)

@callback(
  Output('back-button', 'href'),
  Input('url', 'search'),
)
def update_back_button_href(search):
  query = parse_qs(search.lstrip('?'))
  starter = query.get('starter', [None])[0]
  return f'/viewer?id={starter}'

@callback(
  Output('insight-editor-title', 'children'),
  Output('insight-title', 'value'),
  Output('insight-overview', 'value'),
  Output('insight-visualization', 'src'),
  Output('insight-details', 'value'),
  Input('url', 'search'),
)
def update_details(search):
  placeholder_image = 'https://placehold.co/1200x800?text=Placeholder'
  if not search:
    # new insight, blank editor
    return 'New Insight', '', '', placeholder_image, ''

  # parse params
  query = parse_qs(search.lstrip('?'))
  # look for starter insight
  insight_id = query.get('starter', [None])[0]

  if not insight_id:
    # new insight, blank editor
    return 'New Insight', '', '', placeholder_image, ''

  # load existing insight
  item = next((x for x in insights if x['id'] == insight_id), None)
  if not item:
    return f'New Insight', '', '', placeholder_image, ''

  return item['title'], item['title'], item['overview'], item['image_url'], item['details']
