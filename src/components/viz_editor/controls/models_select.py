import dash_mantine_components as dmc

models = [
  '3',
  '6',
  '7',
  '12',
  '15',
  '29',
  '30',
  '31',
  '32',
  '33',
  '34',
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
