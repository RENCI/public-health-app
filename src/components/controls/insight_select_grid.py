import dash
from dash import ALL, callback, ctx, dcc, html, Input, Output
import dash_mantine_components as dmc
from .options import insights

# create a list of buttons
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

insight_select_grid = html.Div([
  html.H1('Select an Insight'),
  html.Div(
    dmc.SimpleGrid(
      id='insight-select-grid',
      type='container',
      cols=1,
      spacing='lg',
      children=insight_buttons,
      p='lg',
    ), style=dict(height='400px', overflowY='scroll')   
  )
])

@callback(
  Output('insight-select', 'value'),
  Input({'type': 'insight-button', 'index': ALL}, 'n_clicks'),
  prevent_initial_call=True,
)
def update_location(insight_value):
  index = ctx.triggered_id['index']
  if 0 <= index < len(insights):
    return insights[index]
  return dash.no_update
