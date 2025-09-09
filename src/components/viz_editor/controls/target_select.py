import dash_mantine_components as dmc


def target_select(value='Incident Hospitalization'):
  return dmc.Select(
    label='Target',
    placeholder='',
    id='target-select',
    value=value,
    data=[
      dict(label='Incident Hospitalization', value='incident_hospitalization'),
      dict(label='Cumulative Hospitalization', value='cumulative_hospitalization'),
    ],
  )
