import dash_mantine_components as dmc

scenarios = ['77', '78', '79', '80', '81']
options = [{'value': c, 'label': c} for c in scenarios]


def scenarios_select(value=scenarios):
  return dmc.MultiSelect(
    label='Scenarios',
    placeholder='',
    id='scenarios-select',
    value=value,
    data=options,
  )
