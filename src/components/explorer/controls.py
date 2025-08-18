import dash
from dash import callback, dcc, html, Input, Output, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify

grid_cell_style = dict(
  padding='var(--mantine-spacing-sm)',
)

scenarios_select = dmc.MultiSelect(
  label='Scenarios',
  placeholder='',
  id='scenarios-select',
  value=['A', 'B', 'C', 'D', 'E'],
  data=[
    { 'value': 'A', 'label': 'A'},
    { 'value': 'B', 'label': 'B'},
    { 'value': 'C', 'label': 'C'},
    { 'value': 'D', 'label': 'D'},
    { 'value': 'E', 'label': 'E'},
  ],
)

location_select = dmc.Select(
  label='Location',
  placeholder='',
  id='location-select',
  value='US',
  data=[
    'US', 'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado',
    'Connecticut', 'Delaware', 'District of Columbia', 'Florida', 'Georgia',
    'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky',
    'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
    'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
    'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota',
    'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island',
    'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
    'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
  ],
)

target_select = dmc.Select(
  label='Target',
  placeholder='',
  id='target-select',
  value='Incident Hospitalization',
  data=['Incident Hospitalization', 'Cumulative Hospitalization'],
)

age_group_select = dmc.Select(
  label='Age Group',
  placeholder='',
  id='age-group-select',
  value='All Ages',
  data=['All Ages', '0 - 1', '1 - 4', '5 - 64', '65+'],
)

uncertainty_select = dmc.Select(
  label='Uncertainty',
  placeholder='',
  id='uncertainty-select',
  value='Multi',
  data=['None', '50%', '95%', 'Multi'],
)

ensemble_select = dmc.Select(
  label='Ensemble',
  placeholder='',
  id='ensemble-select',
  value='Ensemble',
  data=['Ensemble', 'All'],
)

controls = dmc.Card(
  dmc.Grid(
    children=[
      # dmc.GridCol(scenarios_select, style=grid_cell_style, span=dict(base=12)),
      dmc.GridCol(location_select, style=grid_cell_style, span=dict(base=12)),
      dmc.GridCol(target_select, style=grid_cell_style, span=dict(base=12)),
      dmc.GridCol(age_group_select, style=grid_cell_style, span=dict(base=12)),
      dmc.GridCol(uncertainty_select, style=grid_cell_style, span=dict(base=12)),
      # dmc.GridCol(ensemble_select, style=grid_cell_style, span=dict(base=12)),
    ],
    gutter=0,
  ),
  variant='soft',
  style=dict(height='100%'),
)