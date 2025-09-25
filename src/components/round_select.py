import random

import dash_mantine_components as dmc
from dash import Input, Output, callback

from src.util.data import load_rounds

rounds = load_rounds()

# temp, for round option blurbs
lorem_ispum = [
  'Aliquip ex dolor aliqua sed est ea minim aute in dolor.',
  'Officia incididunt cillum eu minim excepteur proident.',
  'Ullamco aliquip reprehenderit ea proident proident aliquip.',
  'Lorem ipsum quis consectetur deserunt ad quis tempor cupidatat.',
  'Nostrud ut occaecat incididunt sed nulla nostrud est in.',
]

options = [
  dict(
    value=n,
    label=f'Round {rounds[n]["round_number"]}',
    snippet=random.choice(lorem_ispum),
    insights_count=len(rounds[n].get('insights')),
  )
  for n in rounds.keys()
]

sorted_options = sorted(options, key=lambda o: o['label'], reverse=True)


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
  )


@callback(
  Output('selected-round-store', 'data'),
  Input('round-select', 'value'),
)
def update_selected_round_store(selected_round):
  return selected_round
