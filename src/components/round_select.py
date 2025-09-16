from dash import dcc
import dash_mantine_components as dmc

round_numbers = ['19']

options = [{'value': n, 'label': f'Round {n}'} for n in round_numbers]

def round_select(value='19'):
  return dmc.Select(
    placeholder='',
    id='round-select',
    value=value,
    data=options,
    size='xs',
  )

round_store = dcc.Store(id='selected-round-store', data='19')
