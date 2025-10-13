import dash_mantine_components as dmc

from src.components.enums import CertaintyInterval

certainty_values = [v.display_value for v in CertaintyInterval]
options = [{'value': v, 'label': v} for v in certainty_values]


def certainty_select(value='None'):
  return dmc.Select(
    label='Certainty Percent',
    placeholder='',
    id='certainty-select',
    value=value,
    data=options,
  )
