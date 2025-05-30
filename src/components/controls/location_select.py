import dash_mantine_components as dmc
from src import options

location_select = dmc.Select(
  label='Location',
  placeholder='',
  id='location-select',
  value='US',
  data=options.locations,
)