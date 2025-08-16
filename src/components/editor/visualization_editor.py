from dash import callback, dcc, Input, Output, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from .controls import controls

controls_visibility_store = dcc.Store(id='controls-visibility', data=True)  # True = open, False = closed

controls_toggle = dmc.Button(
  'Hide Controls',
  rightSection=DashIconify(icon='feather:chevron-right'),
  id='controls-toggle',
  variant='subtle',
  size='xs',
)

visualization_editor = dmc.Grid(
  children=[
    dmc.GridCol(
      [
        controls_visibility_store,
        dmc.ButtonGroup([
          controls_toggle,
        ], style=dict(justifyContent='flex-end')),
      ],
      span=dict(base=12),
    ),
    dmc.GridCol(
      dmc.Image(id='insight-visualization', src='https://placehold.co/1200x400', radius='sm'),
      id='visualization-column',
      span=8,
    ),
    dmc.GridCol(
      controls,
      id='controls-column',
      span=4,
    )
  ],
  mb=12,
)

# toggle the controls visibility store value when clicking the button
@callback(
  Output('controls-visibility', 'data'),
  Output('controls-toggle', 'children'),
  Output('controls-toggle', 'rightSection'),
  Input('controls-toggle', 'n_clicks'),
  State('controls-visibility', 'data'),
  prevent_initial_call=True
)
def toggle_controls_visibility_store(n_clicks, is_open):
  new_open = not is_open
  new_label = 'Hide Controls' if new_open else 'Show Controls'
  new_icon = DashIconify(icon='feather:chevron-right') if new_open else DashIconify(icon='feather:chevron-left')
  return new_open, new_label, new_icon
