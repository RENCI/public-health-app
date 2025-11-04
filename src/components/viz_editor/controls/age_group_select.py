import dash_mantine_components as dmc

from src.components.enums import AgeGroup

options = [{'value': a.get_input_value(), 'label': a.get_display_value()} for a in AgeGroup]


def age_group_select(value: str = AgeGroup.ALL.get_input_value()):
  return dmc.Select(
    label='Age Group',
    placeholder='',
    id='age-group-select',
    value=value,
    required=True,
    data=options,
  )
