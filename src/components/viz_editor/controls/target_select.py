import dash_mantine_components as dmc


def target_select(value='Incident Hospitalization'):
  return dmc.Select(
    label='Target',
    placeholder='',
    id='target-select',
    value=value,
    data=['Incident Hospitalization', 'Cumulative Hospitalization'],
  )
