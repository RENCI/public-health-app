import dash_mantine_components as dmc

from src.components.enums import CertaintyInterval

options = [v.get_display_value() for v in CertaintyInterval]


def certainty_select(value: str = CertaintyInterval.NONE.get_display_value()):
  return dmc.Select(
    label='Certainty Percent',
    placeholder='',
    id='certainty-select',
    value=value,
    data=options,
    disabled=value is None,
  )
