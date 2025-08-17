from dash import callback, dcc, html, Input, Output, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify

def markdown_editor(
  editor_id='content-editor',
  preview_id='content-preview',
  label='',
):
  callback(
    Output(preview_id, 'children'),
    Input(editor_id, 'n_blur'),
    Input(editor_id, 'value'),  # triggers on page load
    State(editor_id, 'value'),
  )(lambda n_blur, value, state: '## Nothing to preview :(' if not state else state)  
  
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
        dcc.Textarea(id=editor_id, placeholder='Write markdown here...', className='content-editor'),
        value='edit',
      ),
      dmc.TabsPanel(
        dcc.Markdown(id=preview_id, className='content-preview'),
        value='preview',
      ),
    ],
    variant='default',
    radius='sm',
    value='edit',
  )

