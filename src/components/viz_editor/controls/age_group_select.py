import dash_mantine_components as dmc

age_group_select = dmc.Select(
  label='Age Group',
  placeholder='',
  id='age-group-select',
  value='All Ages',
  data=['All Ages', '0 - 1', '1 - 4', '5 - 64', '65+'],
)
