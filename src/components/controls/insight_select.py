import dash
from dash import ALL, callback, ctx, dcc, html, Input, Output, State
import dash_mantine_components as dmc
import plotly.express as px
import pandas as pd
from dash_iconify import DashIconify

from .options import insights

insight_store = dcc.Store('insight-store', data='', storage_type='local')

insight_input = dmc.Textarea(
  id='insight-input',
  label='insight',
  leftSection=DashIconify(icon='feather:crosshair'),
  rightSection=dmc.ActionIcon(
    DashIconify(icon='feather:edit-3'),
    id='edit-insight-button',
    variant='light'
  ),
  value='...',
  autosize=True,
  minRows=2,
  readOnly=True,
  pointer=True,
  style=dict(
    width='100%',
  ),
)

insight_buttons = [
  dmc.Button(
    label,
    id={'type': 'insight-button', 'index': i},
    variant='outline',
    size='sm',
    fullWidth=True,
  )
  for i, label in enumerate(insights)
]

insight_select_grid = html.Div(
  dmc.SimpleGrid(
    id='insight-select-grid',
    type='container',
    cols=1,
    spacing='lg',
    children=insight_buttons,
    p='lg',
  ),
  style=dict(height='400px', overflowY='scroll')   
)

insight_modal = dmc.Modal(
  id='insight-modal',
  opened=False,
  title='insight',
  size='lg',
  children=[
    dcc.Store(id='working-insight-store', data=''),
    html.H1('Select an Insight'),
    insight_select_grid,
  ],
  style=dict(display='flex', gap='2rem'),
)

insight_select = dmc.Group([
  insight_input,
  insight_modal,
])

@callback(
  Output('insight-input', 'value'),
  Input('insight-store', 'data'),
)
def update_input_text(selected_insight):
  return selected_insight or '...'

@callback(
  [Output('insight-modal', 'opened'),
   Output('insight-store', 'data')],
  [Input('edit-insight-button', 'n_clicks'),
   Input({'type': 'insight-button', 'index': ALL}, 'n_clicks')],
  [State('insight-store', 'data'),
   State('insight-modal', 'opened')],
  prevent_initial_call=True
)
def handle_insight_modal(
  edit_insight_clicks,
  clicked_insights,
  stored_insight,
  modal_open
):
  trigger = ctx.triggered_id

  if trigger == 'edit-insight-button':
    return True, stored_insight

  if isinstance(trigger, dict):
    index = trigger.get('index')
    if 0 <= index < len(insights):
      return False, insights[index]

  raise dash.exceptions.PreventUpdate
