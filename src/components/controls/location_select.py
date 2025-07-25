import dash
from dash import callback, ctx, dcc, html, Input, Output, State
import dash_mantine_components as dmc
import plotly.express as px
import pandas as pd
from dash_iconify import DashIconify

from .options import locations

location_store = dcc.Store('location-store', data='US', storage_type='local')

location_input = dmc.TextInput(
  id='location-input',
  label='Location',
  leftSection=DashIconify(icon='feather:map-pin'),
  rightSection=dmc.ActionIcon(
    DashIconify(icon='feather:edit-3'),
    id='edit-location-button',
    variant='light'
  ),
  value='...',
  readOnly=True,
  pointer=True,
  style=dict(
    width='100%',
  ),
)

# filter out the "US" entry
state_locations = [loc for loc in locations if loc['value'] != 'US']
us_button = dmc.Button('Select Entire U.S.', id='us-button', variant='outline', color="default")

# states dataframe
df = pd.DataFrame({
  'state': [loc['value'] for loc in state_locations],
  'label': [loc['label'] for loc in state_locations],
  'value': [1] * len(state_locations)
})

# us states choropleth
def make_figure(highlight_state=None):
  color_column = []
  for state in df['state']:
    if state == highlight_state:
      color_column.append('selected')
    else:
      color_column.append('normal')

  color_df = df.copy()
  color_df['color'] = color_column

  fig = px.choropleth(
    color_df,
    locations='state',
    locationmode='USA-states',
    scope='usa',
    color='color',
    color_discrete_map={
      'selected': '#40c057',
      'normal': '#8af'
    },
    hover_name='label',
  )

  fig.update_traces(
    hoverinfo='none',
    hovertemplate=None,
    marker=dict(line=dict(width=0)),
  )

  fig.update_layout(
    clickmode='event+select',
    coloraxis_showscale=False,
    geo=dict(bgcolor='rgba(0,0,0,0)'),
    margin=dict(l=0, r=0, t=0, b=0),
    showlegend=False
  )

  return fig

location_select_map = dcc.Graph(
  id='us-map',
  figure=make_figure(),
  style={
    'height': '400px',
  },
  config={'displayModeBar': False}
)

location_modal = dmc.Modal(
  id='location-modal',
  opened=False,
  title='Location',
  size='lg',
  children=[
    dcc.Store(id='working-location-store', data=''),
    dmc.Group([html.H1('Select a State or '), us_button]),
    location_select_map,
    dmc.Group([
      dmc.Text('Selected:', id='working-location-label'),
      dmc.Text('...', id='working-location-text'),
      dmc.Box(style=dict(flex=1)),
      dmc.Button('Confirm', id='location-confirm', color='blue'),
      dmc.Button('Cancel', id='location-cancel', variant='outline')
    ], mt='md', justify='flex-end')
  ],
  style=dict(display='flex', gap='2rem'),
)

location_select = dmc.Group([
  location_input,
  location_modal,
])

location_name_lookup = {loc['value']: loc['label'] for loc in locations}

@callback(
  Output('location-store', 'data'),
  Input('location-confirm', 'n_clicks'),
  State('working-location-store', 'data'),
  prevent_initial_call=True,
)
def update_location_store(confirm_cbutton_licks, working_location):
  return working_location

@callback(
  [Output('location-modal', 'opened'),
   Output('working-location-store', 'data'),
   Output('working-location-text', 'children')],
  [Input('edit-location-button', 'n_clicks'),
   Input('location-confirm', 'n_clicks'),
   Input('location-cancel', 'n_clicks'),
   Input('us-map', 'clickData'),
   Input('us-button', 'n_clicks'),
   State('working-location-store', 'data'),
   State('location-store', 'data'),
   State('location-modal', 'opened')],
)
def handle_location_modal(
  location_input_clicks,
  confirm_button_clicks,
  cancel_button_clicks,
  map_click_data,
  us_button_clicks,
  working_location,
  stored_location,
  modal_open
):
  trigger = ctx.triggered_id

  if trigger == 'edit-location-button':
    return True, stored_location, location_name_lookup.get(stored_location)  # pre-fill with existing

  if trigger == 'location-cancel':
    return False, '', ''

  if trigger == 'us-map' and map_click_data:
    selection = location_name_lookup.get(map_click_data['points'][0]['location'])
    return modal_open, map_click_data['points'][0]['location'], selection

  if trigger == 'us-button':
    return modal_open, 'US', 'US'

  if trigger == 'location-confirm':
    return False, '', working_location

  return modal_open, dash.no_update, dash.no_update


@callback(
  Output('us-button', 'leftSection'),
  Output('us-button', 'variant'),
  Output('us-button', 'color'),
  Output('us-button', 'children'),
  Input('working-location-store', 'data'),
  Input('us-button', 'n_clicks'),
)
def style_us_button(working_location, n_clicks):
  if working_location == 'US':
    return DashIconify(icon='feather:check-circle'), 'filled', 'green.7', 'Entire U.S. Selected'
  return DashIconify(icon='feather:circle'), 'outline', 'blue.7', 'Select Entire U.S.'

@callback(
  Output('us-map', 'figure'),
  Input('working-location-store', 'data'),
)
def highlight_selected_state(working_location):
  if working_location and working_location != 'US':
    return make_figure(highlight_state=working_location)
  return make_figure()

@callback(
  Output('location-input', 'value'),
  Input('location-store', 'data'),
)
def update_location_input_label(location_value):
  return location_name_lookup.get(location_value, location_value)
