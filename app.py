from dash import Dash, _dash_renderer
import dash_mantine_components as dmc
from src.theme import DEFAULT_THEME
from src.components.layout import layout

_dash_renderer._set_react_version('18.2.0')

app = Dash(
  external_stylesheets=dmc.styles.ALL,
  use_pages=True,
  pages_folder='src/pages',
)

app.title = 'ACCIDDA'
app.layout = dmc.MantineProvider(
  theme=DEFAULT_THEME,
  id='mantine-provider',
  children=layout,
)

server = app.server

if __name__ == '__main__':
  app.run(debug=True)
