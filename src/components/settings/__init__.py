from dash import html
import dash_mantine_components as dmc
from .theme_toggle import theme_toggle

settings = dmc.Stack(
  [
    html.H3('Settings'),
    dmc.Group(['Color Scheme:', theme_toggle]),
  ],
  id='settings',
  gap='0',
  p='md',
)
