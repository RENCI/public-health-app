import dash_mantine_components as dmc

scenarios = ['1', '2']
options = [{'value': c, 'label': c} for c in scenarios]


def scenarios_select(value=scenarios):
  return dmc.MultiSelect(
    label='Scenarios',
    placeholder='',
    id='scenarios-select',
    value=value,
    data=options,
  )
