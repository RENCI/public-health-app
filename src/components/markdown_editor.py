import dash_mantine_components as dmc
from dash import Input, Output, callback, dcc
from dash.dependencies import MATCH
from dash_iconify import DashIconify
import markdown


def markdown_editor(
  editor_id='content-editor',
  preview_id='content-preview',
  label='',
  initial_value='',
  min_height='6rem',
):
  tabs = [
    dmc.TabsTab('Edit', value='edit', leftSection=DashIconify(icon='feather:edit-3')),
    dmc.TabsTab('Preview', value='preview', leftSection=DashIconify(icon='feather:eye')),
  ]

  if label != '':
    tabs.insert(0, dmc.Text(label, c='var(--mantine-color-blue-text)', size='lg', mr=24))

  return dmc.Tabs(
    [
      dmc.TabsList(tabs, mb=8),
      dmc.TabsPanel(
        dcc.Textarea(
          value=initial_value,
          id={'type': 'editor', 'id': editor_id},
          placeholder='Write markdown here...',
          className='content-editor',
          style=dict(minHeight=min_height),
        ),
        value='edit',
      ),
      dmc.TabsPanel(
        dcc.Markdown(
          markdown.markdown(initial_value, extensions=['extra']),
          dangerously_allow_html=True,
          id={'type': 'preview', 'id': editor_id},
          className='content-preview',
          style=dict(minHeight=min_height),
        ),
        value='preview',
      ),
    ],
    variant='default',
    radius='sm',
    value='edit',
  )


@callback(
  Output({'type': 'preview', 'id': MATCH}, 'children'),
  Input({'type': 'editor', 'id': MATCH}, 'value'),
  prevent_initial_call=True,
)
def update_preview(value):
  return '## Nothing to preview :(' if not value else value