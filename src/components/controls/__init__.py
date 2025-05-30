from dash import callback, dcc, html, Input, Output, State
import dash_mantine_components as dmc
import json 

from .location_select import location_select
from .insight_select import insight_select

controls_store = dcc.Store(id='controls-store', data={})

controls_form = dmc.Stack(
  children=[
    location_select,
    insight_select,
  ],
  gap='md',
)

controls = dmc.Stack(
  children=[
    controls_store,
    html.H3('Controls'),
    controls_form,
  ],
  gap='0',
  p='md',
)

controls_debugger = html.Pre(id='controls-debugger')

@callback(
  Output('controls-store', 'data'),
  Input('location-select', 'value'),
  Input('insight-select', 'value'),
)
def update_controls_store(location, insight):
  return {
    'location': location,
    'insight': insight,
  }

@callback(
  Output('controls-debugger', 'children'),
  Input('controls-store', 'data'),
)
def update_debugger(data):
  return 'controls: ' + json.dumps(data, indent=2)

@callback(
  Output('controls-debugger', 'style'),
  Input('theme-store', 'data'),
)
def set_debugger_style(theme):
  return {
    'whiteSpace': 'pre-wrap',
    'padding': '1rem',
    'backgroundColor': '#ddd' if theme == 'light' else '#333',
    'color': '#333' if theme == 'light' else '#ddd',
  }
