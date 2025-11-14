import dash_mantine_components as dmc
from dash import Dash, _dash_renderer, dcc

from src.components.layout import layout
from src.constants import get_constants
from src.theme import DEFAULT_THEME


def initialize_app_data():
  """Load and initialize all application data at startup."""
  # load constants from JSON file
  constants = get_constants()
  # initialize chart cache
  return constants


# load and return constants/chart cache once at application startup
CONSTANTS = initialize_app_data()

_dash_renderer._set_react_version('18.2.0')
insight_store = dcc.Store(id='selected_insight', storage_type='local')

external_stylesheets = [
  *dmc.styles.ALL,
  'https://fonts.googleapis.com/css2?family=Inter:wght@100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&display=swap',
]

app = Dash(
  external_stylesheets=external_stylesheets,
  use_pages=True,
  pages_folder='src/pages',
  suppress_callback_exceptions=True,
)

app.title = 'ACCIDDA'
app.layout = dmc.MantineProvider(
  theme=DEFAULT_THEME,
  id='mantine-provider',
  children=[
    layout,
    insight_store,
  ],
)

server = app.server

if __name__ == '__main__':
  app.run(debug=True)
