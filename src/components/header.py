from dash import callback, dcc, Input, Output, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify

logo = dmc.Text('[ 📈 ACCIDDA ]', c='blue')

aside_toggle_button = dmc.ActionIcon(
  id='aside-toggle',
  variant='light',
  size='lg',
  children=DashIconify(icon='feather:settings', width=20),
)

header = dmc.Flex(
  children=[
    dmc.Group([
      dmc.Burger(id='navbar-toggle', size='sm', opened=False),
      logo,
    ]),
    dmc.Group([
      dmc.Burger(id='aside-toggle', size='sm', opened=False),
    ]),
  ],
  justify='space-between',
  style={'flex': 1},
  h='100%',
  px='md',
)
