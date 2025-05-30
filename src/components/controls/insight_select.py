import dash_mantine_components as dmc
from src import options

insight_select = dmc.Select(
  label='Insight',
  placeholder='',
  id='insight-select',
  value='When immunescape reaches a maximum',
  data=options.insights,
)
