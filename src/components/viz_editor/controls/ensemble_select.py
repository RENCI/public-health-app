import dash_mantine_components as dmc


def ensemble_select(value='Ensemble'):
  return dmc.Select(
    label='Ensemble',
    placeholder='',
    id='ensemble-select',
    value=value,
    data=['Ensemble', 'All'],
    allowDeselect=False,
  )
