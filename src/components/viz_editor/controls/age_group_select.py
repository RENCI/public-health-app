import dash_mantine_components as dmc

def age_group_select(value='All Ages'):
  return dmc.Select(
    label='Age Group',
    placeholder='',
    id='age-group-select',
    value=value,
    data=['All Ages', '0 - 1', '1 - 4', '5 - 64', '65+'],
  )
