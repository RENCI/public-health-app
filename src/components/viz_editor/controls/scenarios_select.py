import dash_mantine_components as dmc

values = ['A', 'B', 'C', 'D', 'E']
options = [{'value': c, 'label': c} for c in values]

scenarios_select = dmc.MultiSelect(
  label='Scenarios',
  placeholder='',
  id='scenarios-select',
  value=values,
  data=options,
)
