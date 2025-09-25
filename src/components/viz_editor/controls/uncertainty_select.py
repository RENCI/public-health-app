import dash_mantine_components as dmc

from src.components.enums import Uncertainty

uncertainty_values = [v.display_value for v in Uncertainty]
options = [{'value': v, 'label': v} for v in uncertainty_values]


def uncertainty_select(value='None'):
  return dmc.Select(
    label='Uncertainty',
    placeholder='',
    id='uncertainty-select',
    value=value,
    data=options,
  )
