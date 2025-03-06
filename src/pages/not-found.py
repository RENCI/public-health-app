import dash
from dash import html

header = html.H1('😕 404, Not found')

layout = html.Div([
  header,
])

dash.register_page(__name__)
