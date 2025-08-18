from dash import callback, dcc, html, Input, Output, State
from dash.dependencies import MATCH
import dash_mantine_components as dmc
from dash_iconify import DashIconify

def markdown_editor(
  explorer_id='content-editor',
  preview_id='content-preview',
  label='',
  initial_value='',
):
  tabs = [
    dmc.TabsTab('Edit', value='edit', leftSection=DashIconify(icon='feather:edit-3')),
    dmc.TabsTab('Preview', value='preview', leftSection=DashIconify(icon='feather:eye')),
  ]

  if (label != ''):
    tabs.insert(0, dmc.Text(label, c='var(--mantine-color-blue-text)', size='lg', mr=24))

  return dmc.Tabs(
    [
      dmc.TabsList(tabs, mb=8),
      dmc.TabsPanel(
        dcc.Textarea(value=initial_value, id={'type': 'explorer', 'id': explorer_id}, placeholder='Write markdown here...', className='content-editor'),
        value='edit',
      ),
      dmc.TabsPanel(
        dcc.Markdown(initial_value, id={'type': 'preview', 'id': explorer_id}, className='content-preview'),
        value='preview',
      ),
    ],
    variant='default',
    radius='sm',
    value='edit',
  )

@callback(
  Output({'type': 'preview', 'id': MATCH}, 'children'),
  Input({'type': 'explorer', 'id': MATCH}, 'value'),
)
def update_preview(value):
  return '## Nothing to preview :(' if not value else value
