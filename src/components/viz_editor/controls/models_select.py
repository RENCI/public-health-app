import dash_mantine_components as dmc

models = [
  '1',
  '3',
  '5',
  '6',
  '7',
  '9',
  '18',
]
options = [{'value': m, 'label': m} for m in models]


def models_select(value=['18']):
  return dmc.MultiSelect(
    label='Models',
    placeholder='',
    id='models-select',
    value=value,
    data=options,
  )
