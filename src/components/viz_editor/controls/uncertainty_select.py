import dash_mantine_components as dmc

def uncertainty_select(value='None'):
  return dmc.Select(
    label='Uncertainty',
    placeholder='',
    id='uncertainty-select',
    value=value,
    data=['None', '50%', '95%', 'Multi'],
  )
