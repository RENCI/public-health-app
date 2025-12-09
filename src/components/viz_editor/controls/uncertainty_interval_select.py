import dash_mantine_components as dmc

from src.components.enums import UncertaintyInterval

options = [v.get_display_value() for v in UncertaintyInterval]


def uncertainty_interval_select(value: str = UncertaintyInterval.NONE.get_display_value(), disabled=False):
  return dmc.Select(
    label='Uncertainty Interval',
    placeholder='',
    id='uncertainty-interval-select',
    value=value,
    data=options,
    disabled=disabled,
    comboboxProps={"shadow": "md"},
  )
