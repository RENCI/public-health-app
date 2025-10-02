import dash_mantine_components as dmc

options = [
  {'value': 'Ensemble', 'label': 'Ensemble'},
  {'value': 'Ensemble_LOP', 'label': 'Ensemble_LOP'},
  {'value': 'Individual Models', 'label': 'Individual Models'},
]


def ensemble_select(value='Ensemble'):
  return dmc.Select(
    label='Ensemble',
    placeholder='',
    id='ensemble-select',
    value=value,
    data=options,
    allowDeselect=False,
  )
