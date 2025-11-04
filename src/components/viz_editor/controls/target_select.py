import dash_mantine_components as dmc

from src.components.enums import Target

options = [{'value': t.get_input_value(), 'label': t.get_display_value()} for t in Target]


def target_select(value: str = Target.INCIDENT_HOSPITALIZATION.get_input_value()):
  return dmc.Select(
    label='Target',
    placeholder='',
    id='target-select',
    value=value,
    required=True,
    data=options,
  )
