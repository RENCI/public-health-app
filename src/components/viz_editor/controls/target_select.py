import dash_mantine_components as dmc

target_select = dmc.Select(
  label='Target',
  placeholder='',
  id='target-select',
  value='Incident Hospitalization',
  data=['Incident Hospitalization', 'Cumulative Hospitalization'],
)
