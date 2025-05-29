from dash import callback, dcc, Input, Output, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from src.components.theme_toggle import theme_toggle
from src.components.theme_toggle import theme_toggle

aside = dmc.Stack(
  [
    'settings',
    theme_toggle,
  ],
  id='settings',
  gap='0',
)
