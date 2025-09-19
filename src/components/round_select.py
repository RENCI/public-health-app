from dash import callback, Input, Output
import dash_mantine_components as dmc
from ..util.data import load_rounds

rounds = load_rounds()

options = [dict(
  value=n,
  label=f'Round {rounds[n]['round_number']}',
  detail='X insights',
) for n in rounds.keys()]

def round_select(value='19'):
  return dmc.Select(
    placeholder='',
    id='round-select',
    value=value,
    data=options,
    size='xs',
    allowDeselect=False,
    renderOption={'function': 'renderRoundOption'},
    style=dict(width='300px'),
  )

@callback(
  Output('selected-round-store', 'data'),
  Input('round-select', 'value'),
)
def update_selected_round_store(selected_round):
  return selected_round
