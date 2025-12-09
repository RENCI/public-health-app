import dash_mantine_components as dmc

from src.components.enums import ChartLayout

options = [{
  'value': l.get_input_value(),
  'label': l.get_display_value()
} for l in ChartLayout]

def layout_select(value: str = 'stack'):
  return dmc.Select(
    label='Layout',
    placeholder='',
    id='chart-layout-select',
    value=value,
    data=options,
    allowDeselect=False,
  )
