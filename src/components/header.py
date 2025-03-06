from dash import callback, dcc, Input, Output, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from src.components.theme_toggle import theme_toggle

logo = dmc.Text('[ 📈 ACCIDDA ]', c='blue')

header = dmc.Flex(
  children=[
    dmc.Group([dmc.Burger(id='burger', size='sm', hiddenFrom='sm', opened=False), logo]),
    dmc.Group([theme_toggle]),
  ],
  justify='space-between',
  style={'flex': 1},
  h='100%',
  px='md',
)
