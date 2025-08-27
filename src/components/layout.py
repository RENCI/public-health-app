import dash
from dash import callback, ctx, dcc, Input, Output, State
import dash_mantine_components as dmc
from src.components.header import header
from src.components.notifications import notifications

custom_insights_store = dcc.Store(id='custom-insights-store', data=[], storage_type='local')

layout = dmc.AppShell(
  [
    custom_insights_store,
    dcc.Location(id='url', refresh=False),
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
