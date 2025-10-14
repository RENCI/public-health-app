import dash_mantine_components as dmc

from src.components.enums import AgeGroup

age_ranges = list(AgeGroup)
options = [{'value': a.input_value, 'label': a.display_value} for a in age_ranges]


def age_group_select(value='0-130'):
  return dmc.Select(
    label='Age Group',
    placeholder='',
    id='age-group-select',
    value=value,
    required=True,
    data=options,
  )
