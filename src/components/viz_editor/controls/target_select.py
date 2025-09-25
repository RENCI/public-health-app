import dash_mantine_components as dmc

from src.components.enums import Target

targets = list(Target)
options = [{'value': t.value, 'label': t.value} for t in targets]


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
