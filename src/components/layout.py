import dash
from dash import callback, dcc, Input, Output, State
from src.components.header import header
from src.components.menu import menu
import dash_mantine_components as dmc

layout = dmc.AppShell(
  [
    dcc.Location(id='url', refresh=False),
    dmc.AppShellHeader(header),
    dmc.AppShellNavbar(menu, id='navbar'),
    dmc.AppShellMain(dash.page_container, id='page-content'),
  ],
  header={'height': 60},
  padding='md',
  navbar={
    'width': 250,
    'breakpoint': 'sm',
    'collapsed': {'mobile': True},
  },
  id='appshell',
)

@callback(
  Output('appshell', 'navbar'),
  Input('burger', 'opened'), # defined in header.py
  State('appshell', 'navbar'),
)
def toggle_navbar(opened, navbar):
  navbar['collapsed'] = {'mobile': not opened}
  return navbar
