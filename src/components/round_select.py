import dash_mantine_components as dmc

round_numbers = ['19']

options = [dict(value=n, label=f'Round {n}', detail='X insights') for n in round_numbers]

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
