import dash_mantine_components as dmc

values = ['A', 'B', 'C', 'D', 'E']
options = [{'value': c, 'label': c} for c in values]


def scenarios_select(value=values):
  return dmc.MultiSelect(
    label='Scenarios',
    placeholder='',
    id='scenarios-select',
    value=value,
    data=options,
  )
