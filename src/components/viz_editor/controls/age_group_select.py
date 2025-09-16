import dash_mantine_components as dmc

age_ranges = ['0-0.99', '1-4', '5-64', '65-130', '0-130']

def age_group_select(value='0-130'):
  return dmc.Select(
    label='Age Group',
    placeholder='',
    id='age-group-select',
    value=value,
    data=age_ranges,
  )
