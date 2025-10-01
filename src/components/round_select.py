from dash import callback, Input, Output
import dash_mantine_components as dmc
from ..util.data import load_rounds

rounds = load_rounds()

options = [
  dict(
    value=n,
    round_number=rounds[n]['round_number'],
    label=f'Round {rounds[n]["round_number"]}',
    snippet=rounds[n]['name'],
    insights_count=len(rounds[n].get('insights')),
  )
  for n in rounds.keys()
]

sorted_options = sorted(options, key=lambda o: o['round_number'], reverse=True)


def round_select(value='19'):
  return dmc.Select(
    placeholder='',
    id='round-select',
    value=value,
    data=sorted_options,
    size='xs',
    allowDeselect=False,
    renderOption={'function': 'renderRoundOption'},
    style=dict(width='300px'),
    withScrollArea=False,
  )


@callback(
  Output('selected-round-store', 'data'),
  Input('round-select', 'value'),
)
def update_selected_round_store(selected_round):
  return selected_round
