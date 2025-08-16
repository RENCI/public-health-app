from dash import html, register_page

register_page(__name__)

header = html.H1('😕 404, Not found')

layout = html.Div([
  header,
])
