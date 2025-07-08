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

def create_insight_button(title, description, index):
  return dmc.Paper(
    children=[
      dmc.Group([
        dmc.Button(
          children='Select',
          id={'type': 'insight-button', 'index': index},
          rightSection=DashIconify(icon='feather:check'),
          variant='light',
          size='xs',
        ),
        dmc.Text(title, fz='md', style=dict(flex=1)),
        dmc.Button(
          DashIconify(icon='feather:info'),
          id=f'collapse-insight-{index}',
          size='xs',
          variant='subtle',
        ),
      ]),
      dmc.Collapse(
        children=description,
        id=f'insight-button-{index}',
        opened=False,
        p='sm',
      ),
    ],
    p="xs",
    radius="sm",
    withBorder=True,
  )

insight_buttons = [create_insight_button(insight['title'], insight['description'], i) for i, insight in enumerate(insights)]

insight_select_grid = html.Div(
  dmc.SimpleGrid(
    id='insight-select-grid',
    type='container',
    cols=1,
    spacing='lg',
    children=[
      *insight_buttons,
      dcc.Store(id='collapse-state-store', data={}),
    ],
    p='lg',
  ),
  style=dict(height='400px', overflowY='scroll')   
)

insight_modal = dmc.Modal(
  id='insight-modal',
  opened=False,
  title='Select an Insight',
  size='lg',
  children=[
    dcc.Store(id='working-insight-store', data=''),
    insight_select_grid,
  ],
  style=dict(display='flex', gap='2rem'),
)

insight_select = dmc.Group([
  insight_input,
  insight_modal,
])

@callback(
  Output('collapse-state-store', 'data'),
  Input({'type': 'insight-button', 'index': ALL}, 'id'),  # dummy input to register components
  [Input(f'collapse-insight-{i}', 'n_clicks') for i in range(len(insights))],
  State('collapse-state-store', 'data'),
  prevent_initial_call=True
)
def toggle_collapse(_, *args):
  collapse_state = args[-1] or {}
  triggered = ctx.triggered_id

  if triggered and isinstance(triggered, str) and triggered.startswith('collapse-insight-'):
    index = int(triggered.split('-')[-1])
    current = collapse_state.get(str(index), False)
    collapse_state[str(index)] = not current
    return collapse_state

  raise dash.exceptions.PreventUpdate

for i in range(len(insights)):
  @callback(
    Output(f'insight-button-{i}', 'opened'),
    Input('collapse-state-store', 'data')
  )
  def update_collapse(collapse_state, i=i):
    return collapse_state.get(str(i), False)

@callback(
  Output('insight-input', 'value'),
  Input('insight-store', 'data'),
)
def update_input_text(selected_insight):
  return selected_insight['title'] or '...'

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
