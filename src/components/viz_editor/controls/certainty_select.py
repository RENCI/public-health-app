import dash_mantine_components as dmc

from src.components.enums import CertaintyInterval

options = [{'value': v.get_bounds(), 'label': v.get_display_value()} for v in CertaintyInterval]


def certainty_select(value: list[tuple[float, float]] = CertaintyInterval.NONE.get_bounds()):
  return dmc.Select(
    label='Certainty Percent',
    placeholder='',
    id='certainty-select',
    value=value,
    data=options,
  )
