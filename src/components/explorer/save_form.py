from dash import callback, dcc, Input, Output, State
import dash_mantine_components as dmc
from urllib.parse import parse_qs
from dash_iconify import DashIconify
from src.components.explorer.metadata_editor import metadata_editor

metadata_editor = dmc.Stack([
  dmc.TextInput(
    id='insight-title', 
    label='Title', 
  ),
  dmc.Textarea(
    id='insight-overview',
    label='Overview',
    autosize=True,
    minRows=5,
  ),
], gap=24)

save_modal = dmc.Modal(
  title='Save Insight',
  id='save-modal',
  size='lg',
  children=[
    dmc.Divider(mb=12),
    metadata_editor,
    dmc.Space(h=48),
    dmc.Group(
      [
        dmc.Button(
          'Cancel',
          leftSection=DashIconify(icon='feather:x'),
          color='crimson',
          variant='outline',
          id='modal-close-button',
        ),
        dcc.Link(
          dmc.Button(
            'Save',
            leftSection=DashIconify(icon='feather:check'),
            id='save-button',
          ),
          id='save-link',
          href='/',
        ),
      ],
      justify='flex-end',
    ),
  ],
)

modal_toggle_button = dmc.Button(
  'Save as New Insight',
  leftSection=DashIconify(icon='feather:save'),
  size='lg',
  id='modal-open-button',
)

save_form = dmc.Center(
  style=dict(height=300, width='100%'),
  children=[modal_toggle_button, save_modal],
)

@callback(
  Output('save-link', 'href'), # temp send back to original
  Input('url', 'search')
)
def add_save_href(search):
  query = parse_qs(search.lstrip('?'))
  insight_id = query.get('starter', [None])[0]
  return f'/viewer?id={insight_id}'

@callback(
  Output('save-modal', 'opened'),
  Input('modal-open-button', 'n_clicks'),
  Input('modal-close-button', 'n_clicks'),
  Input('save-button', 'n_clicks'),
  State('save-modal', 'opened'),
  prevent_initial_call=True,
)
def modal_demo(nc1, nc2, nc3, opened):
  return not opened