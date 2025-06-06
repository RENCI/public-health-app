import dash
from dash import callback, ctx, dcc, html, Output, Input, State
import dash_mantine_components as dmc

from .location_select import location_select, location_store
from .insight_select import insight_select, insight_store

controls_form = dmc.Stack(
  children=[
    location_store, location_select,
    insight_store, insight_select,
  ],
  gap='md',
)

controls = dmc.Stack(
  children=[
    html.H3('Controls'),
    controls_form,
  ],
  gap='0',
  p='md',
)
