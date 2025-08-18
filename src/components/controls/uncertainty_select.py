import dash_mantine_components as dmc

uncertainty_select = dmc.Select(
  label='Uncertainty',
  placeholder='',
  id='uncertainty-select',
  value='Multi',
  data=['None', '50%', '95%', 'Multi'],
)
