import dash_mantine_components as dmc
from dash import Input, Output, callback, exceptions

from src.components.chart import DEFAULT_CONTROL_VALUES
from src.util.data import load_rounds

rounds = load_rounds()

options = [
  dict(
    value=n,
    round_number=rounds[n]['round_number'],
    label=f'Round {rounds[n]["round_number"]}',
    sublabel=f'Round completed: {rounds[n]["date"]}',
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
    size='md',
    allowDeselect=False,
    renderOption={'function': 'renderRoundOption'},
    style=dict(width='300px'),
    withScrollArea=False,
    variant='default',
  )


@callback(
  Output('selected-round-store', 'data'),
  Input('round-select', 'value'),
)
def update_selected_round_store(selected_round):
  return selected_round


@callback(
  Output('chart-controls-store', 'data', allow_duplicate=True),
  Input('round-select', 'value'),
  prevent_initial_call=True,
)
def update_chart_controls_for_round(round_number: str):
  if not round_number:
    raise exceptions.PreventUpdate
  return DEFAULT_CONTROL_VALUES | {
    'round_num': int(round_number),
  }


@callback(
  Output('_pages_location', 'pathname', allow_duplicate=True),
  Input('round-select', 'value'),
  prevent_initial_call=True,
)
def update_url_after_round_change(round_number):
  if not round_number:
    return exceptions.PreventUpdate

  return '/'
