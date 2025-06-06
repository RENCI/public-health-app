from dash import callback, dcc, html, Output, Input
import json

controls_debugger = html.Pre(id='controls-debugger')

@callback(
  Output('controls-debugger', 'children'),
  Input('location-store', 'data'),
  Input('insight-store', 'data'),
  prevent_initial_call=True,
)
def update_debugger_content(location, insight):
  data = dict(location=location, insight=insight)
  return 'controls: ' + json.dumps(data, indent=2)

@callback(
  Output('controls-debugger', 'style'),
  Input('theme-store', 'data'),
)
def align_debugger_style_with_theme(theme):
  is_light = theme == 'light'
  return {
    'whiteSpace': 'pre-wrap',
    'padding': '1rem',
    'backgroundColor': '#ddd' if is_light else '#333',
    'color': '#333' if is_light else '#ddd',
  }
