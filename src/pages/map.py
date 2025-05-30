import dash
from dash import html, dcc, Input, Output, callback
import dash_mantine_components as dmc
import plotly.express as px
import pandas as pd
from src.options import locations

# Register page
dash.register_page(__name__)

# Sample data: US states
df = pd.DataFrame({
  'state': locations,
  'value': list(range(1, len(locations) + 1))
})

# Create Plotly figure
fig = px.choropleth(
  df,
  locations='state',
  locationmode='USA-states',
  color='value',
  scope='usa',
  color_continuous_scale='Blues'
)
fig.update_layout(clickmode='event+select', margin=dict(l=0, r=0, t=0, b=0))

# Layout
layout = html.Div([
  html.H1('Select your state'),
  dcc.Graph(id='us-map', figure=fig, style={'height': '500px'}),
  dcc.Store(id='selected-state'),
  dmc.Text(id='state-output', fw=500, size='lg', style={'marginTop': '1rem'})
])

# Callback to update selected state in Store
@callback(
  Output('selected-state', 'data'),
  Input('us-map', 'clickData')
)
def update_selected_state(click_data):
  if click_data:
    state = click_data['points'][0]['location']
    return state
  return dash.no_update

# Callback to display selected state text
@callback(
  Output('state-output', 'children'),
  Input('selected-state', 'data')
)
def display_selected_state(selected_state):
  if selected_state:
    return f"Selected state: {selected_state}"
  return "Click a state to select it."
