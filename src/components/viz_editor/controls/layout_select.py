import dash_mantine_components as dmc


options = [
  'Grid',
  'Stack',
]


def layout_select(value: str = 'Stack'):
  return dmc.Select(
    label='Layout',
    placeholder='',
    id='layout-select',
    value=value,
    data=options,
    allowDeselect=False,
  )
