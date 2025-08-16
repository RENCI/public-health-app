from dash import callback, dcc, html, Input, Output, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from .theme_toggle import theme_toggle

logo = dcc.Link(dmc.Text('[ 📈 ACCIDDA ]', c='blue'), href='/', style=dict(textDecoration='none'))

header = dmc.Flex(
  children=[
    logo,
    dmc.Group([
      theme_toggle,
      dmc.Burger(id='aside-toggle', size='sm', opened=False, style=dict(display='none')),
      # ^ this button is purely here prevent an error thrown by the callback in /editor
      # that actually uses a duplicate of this button defined in that view.
      # perhaps not the most elegant, but it keeps the callback happy. :/
      # todo: consider nested AppShells
    ]),
  ],
  align='center',
  justify='space-between',
  style={'flex': 1},
  h='100%',
  px='md',
)
