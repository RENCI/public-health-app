from dash import callback, ctx, dcc, html, Input, no_update, Output, register_page, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from src.data.insights import insights
from src.data.templates import templates
from src.components.markdown_editor import markdown_editor
from src.components.editor import save_form, visualization_editor

register_page(__name__, path_template='/editor/<insight_id>', name='Insight Editor')

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
    dmc.Title('Insight Editor', order=1, mt=24),
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
  Input('url', 'pathname')
)
def add_edit_href(pathname):
  insight_id = pathname.split('/')[-1]
  return f'/viewer/{insight_id}'

@callback(
  Output('insight-title', 'value'),
  Output('insight-overview', 'value'),
  Output('insight-visualization', 'src'),
  Output('insight-details', 'value'),
  Input('url', 'pathname'),
)
def update_details(pathname):
  insight_id = pathname.split('/')[-1]
  item = next((x for x in insights if x['id'] == insight_id), None)
  if not item:
    return 'Insight not found', '', '', ''
  return item['title'], item['overview'], item['image_url'], item['details']

# update layout based on store value
@callback(
  Output('visualization-column', 'span'),
  Output('controls-column', 'span'),
  Output('controls-column', 'style'),
  Input('controls-visibility', 'data')
)
def update_sidebar_display(is_open):
  if is_open:
    return 8, 4, {}
  else:
    return 12, 0, {'display': 'none'}
