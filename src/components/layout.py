import dash
from dash import callback, ctx, dcc, Input, Output, State
import dash_mantine_components as dmc
from src.components.header import header

layout = dmc.AppShell(
  [
    dcc.Location(id='url', refresh=False),
    dmc.AppShellHeader(header),
    dmc.AppShellMain(dash.page_container, id='page-content'),
  ],
  header={'height': 60},
  padding='md',
  aside={
    'width': 250,
    'breakpoint': 'sm',
    'collapsed': {'mobile': True, 'desktop': True},
  },
  id='appshell',
)
