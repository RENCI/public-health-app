from dash import callback, dcc, Input, Output, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from src.components.theme_toggle import theme_toggle

nav_items = [
  {'label': 'Home', 'href': '/', 'icon': 'feather:home'},
]

def nav_link(label, href, icon, active):
  return dmc.NavLink(
    href=href,
    label=label,
    leftSection=icon,
    rightSection=DashIconify(icon='feather:chevron-right'),
    # variant='filled' if active else 'subtle' # does not work ?
    # ...so we'll manually stick styles in here.
    style={'color': 'var(--mantine-color-anchor)' if active else 'var(--mantine-color-text)'},
  )

menu = dmc.Stack(children= [], id='menu', gap='0')

# style the active link
@callback(
  Output('menu', 'children'),
  Input('url', 'pathname'),
)
def update_menu(pathname):
  return [nav_link(
    label=item['label'],
    href=item['href'],
    icon=DashIconify(icon=item['icon']),
    active=pathname == item['href'],
  ) for item in nav_items]