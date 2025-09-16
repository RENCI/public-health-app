import dash_mantine_components as dmc

round_numbers = ['19']

def round_select(value='19'):
  return dmc.Select(
    label='Round',
    placeholder='',
    id='round-select',
    value=value,
    data=round_numbers,
  )
