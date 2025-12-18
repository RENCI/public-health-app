import dash_mantine_components as dmc

options = [
  'Ensemble',
  'Ensemble_LOP',
  'Individual Models',
]


def ensemble_select(value: str = 'Ensemble'):
  return dmc.Select(
    label='Ensemble',
    placeholder='',
    id='ensemble-select',
    value=value,
    data=options,
    allowDeselect=False,
    comboboxProps={'shadow': 'md'},
  )
