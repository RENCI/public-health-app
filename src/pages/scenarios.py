import dash
from dash import callback, dcc, html, Input, Output
import dash_mantine_components as dmc
import json

header = html.H1('Scenarios')

emphasis_border = f'1px dashed {dmc.DEFAULT_THEME['colors']['indigo'][2]}'

grid_cell_style = {
  'border': emphasis_border,
  'padding': 'var(--mantine-spacing-sm)',
}

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

toolbar = dmc.Grid(
  children=[
    dmc.GridCol(scenarios_select, style=grid_cell_style, span={  'base': 12, 'sm': 12, 'md': 5, 'xl': 3 }),
    dmc.GridCol(location_select, style=grid_cell_style, span={   'base': 12, 'sm': 3,  'md': 2, 'xl': 3 }),
    dmc.GridCol(target_select, style=grid_cell_style, span={     'base': 12, 'sm': 5,  'md': 5, 'xl': 3 }),
    dmc.GridCol(age_group_select, style=grid_cell_style, span={  'base': 12, 'sm': 4,  'md': 2, 'xl': 1 }),
    dmc.GridCol(uncertainty_select, style=grid_cell_style, span={'base': 12, 'sm': 6,  'md': 5, 'xl': 1 }),
    dmc.GridCol(ensemble_select, style=grid_cell_style, span={   'base': 12, 'sm': 6,  'md': 5, 'xl': 1 }),
  ],
  gutter=0,
)

selection_debug = dmc.Code(
  id='debug-filters',
  style={
    'whiteSpace': 'pre-wrap',
    'padding': 'var(--mantine-spacing-sm)',
    'fontSize': '60%',
    'borderRadius': '0',
    'backgroundColor': 'transparent',
    'margin': 'var(--mantine-spacing-sm) 0',
    'border': emphasis_border,
  },
  block=True,
  variant='outlined',
)

#

layout = html.Div([
  header,
  toolbar,
  selection_debug,
  dcc.Store(id='filters-store', data={}),
])

dash.register_page('scenarios', layout=layout, path='/scenarios')

# store selections
@callback(
  Output('filters-store', 'data'),
  Input('scenarios-select', 'value'),
  Input('location-select', 'value'),
  Input('target-select', 'value'),
  Input('age-group-select', 'value'),
  Input('uncertainty-select', 'value'),
  Input('ensemble-select', 'value'),
)
def update_store(scenarios, location, target, age_group, uncertainty, ensemble):
  return {
    'scenarios': scenarios,
    'location': location,
    'target': target,
    'age_group': age_group,
    'uncertainty': uncertainty,
    'ensemble': ensemble,
  }

# update filter selection state summary
@callback(
  Output('debug-filters', 'children'),
  Input('filters-store', 'data'),
  # prevent_initial_call=True,
)
def update_debug_contents(data_store):
  return json.dumps(data_store, indent=2)
