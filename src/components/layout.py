import dash
import dash_mantine_components as dmc
from dash import dcc

from src.components.header import header
from src.components.notifications import notifications

custom_insights_store = dcc.Store(id='custom-insights-store', data=[], storage_type='local')

layout = dmc.AppShell(
  [
    custom_insights_store,
    dcc.Store(id='selected-round-store', storage_type='local', data='19'),
    dcc.Clipboard(id='clipboard', style=dict(display='none')),
    dcc.Location(id='url', refresh='callback-nav'),
    dmc.AppShellHeader(header),
    dmc.AppShellMain(dash.page_container, id='page-content'),
    notifications,
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
