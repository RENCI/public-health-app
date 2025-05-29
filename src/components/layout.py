import dash
from dash import callback, dcc, Input, Output, State
from src.components.header import header
from src.components.menu import menu
from src.components.aside import aside
import dash_mantine_components as dmc

layout = dmc.AppShell(
  [
    dcc.Location(id='url', refresh=False),
    dmc.AppShellHeader(header),
    dmc.AppShellNavbar(menu, id='navbar'),
    dmc.AppShellAside(aside, id='aside'),
    dmc.AppShellMain(dash.page_container, id='page-content'),
  ],
  header={'height': 60},
  padding='md',
  navbar={
    'width': 250,
    'breakpoint': 'sm',
    'collapsed': {'mobile': True, 'desktop': True},
  },
  aside={
    'width': 250,
    'breakpoint': 'sm',
    'collapsed': {'mobile': True, 'desktop': False},
  },
  id='appshell',
)

@callback(
  Output('appshell', 'navbar'),
  Output('navbar-toggle', 'opened'),
  Input('navbar-toggle', 'opened'),
  State('appshell', 'navbar'),
)
def toggle_navbar(opened, navbar):
  is_collapsed = not opened
  # Collapse on both mobile and desktop based on opened state
  navbar['collapsed'] = {
    'mobile': is_collapsed,
    'desktop': is_collapsed,
  }
  return navbar, opened

@callback(
  Output('appshell', 'aside'),
  Output('aside-toggle', 'opened'),
  Input('aside-toggle', 'opened'),
  State('appshell', 'aside'),
)
def toggle_aside(opened, aside):
  is_collapsed = not opened
  # Collapse on both mobile and desktop based on opened state
  aside['collapsed'] = {
    'mobile': is_collapsed,
    'desktop': is_collapsed,
  }
  return aside, opened
