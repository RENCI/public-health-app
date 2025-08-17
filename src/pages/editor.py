from dash import callback, ctx, dcc, exceptions, html, Input, no_update, Output, register_page, State
import dash_mantine_components as dmc
from urllib.parse import parse_qs
from dash_iconify import DashIconify
from src.data.insights import get_insight
from src.data.templates import templates
from src.components.markdown_editor import markdown_editor
from src.components.editor import save_form, visualization_editor
from src.util.get_query_param import get_query_param

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

def layout(starter=None):
  item = get_insight(starter) or {}
  details = item.get('details', '')
  title = item.get('title', '')
  overview = item.get('overview', '')
  image_url = item.get('image_url', '')

  return dmc.Container(
    [
      toolbar,
      dmc.Title(f'Insight Editor: {title}', order=1, mt=24),
      visualization_editor(image_url),
      dmc.Space(h=24),
      markdown_editor(
        label='Insight Details',
        initial_value=details,
        editor_id='insight-details',
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
  starter = get_query_param(search, 'starter')
  if not starter:
    raise exceptions.PreventUpdate
  return f'/viewer?id={starter}' if starter else '/'

# @callback(
#   Output('insight-editor-title', 'children'),
#   Output('insight-title', 'value'),  # in the save form
#   Output('insight-overview', 'value'),  # in the save form
#   Output('insight-visualization', 'src'),
#   Output('insight-details', 'value'),
#   Input('url', 'search'),
# )
# def hydrate_insight_template(search):
#   placeholder_image = 'https://placehold.co/1200x800?text=Placeholder'
#   if not search:
#     # new insight, blank editor
#     return 'New Insight', '', '', placeholder_image, ''

#   # we have params. look for starter insight
#   insight_id = get_query_param(search, 'starter')
#   item = get_insight(insight_id)

#   # if we can find
#   if not item:
#     return f'New Insight', '', '', placeholder_image, ''

#   # return found insight details
#   return f'{item['title']}', item['title'], item['overview'], item['image_url'], item['details']
