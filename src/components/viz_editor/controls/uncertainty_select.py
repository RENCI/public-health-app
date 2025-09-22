import dash_mantine_components as dmc

uncertainty_values = ['None', '50%', '95%', 'Multi']
options = [{'value': v, 'label': v} for v in uncertainty_values]


def uncertainty_select(value='None'):
  return dmc.Select(
    label='Uncertainty',
    placeholder='',
    id='uncertainty-select',
    value=value,
    data=options,
  )
