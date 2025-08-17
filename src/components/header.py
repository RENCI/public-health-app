from dash import callback, dcc, html, Input, Output, State
import dash_mantine_components as dmc
import re
from dash_iconify import DashIconify
from .theme_toggle import theme_toggle

logo = dcc.Link(dmc.Text('[ 📈 ACCIDDA ]', c='blue'), href='/', style=dict(textDecoration='none'))

header = dmc.Flex(
  children=[
    dmc.Group([
      logo,
      dmc.Anchor('Viewer', href='/', id='nav-viewer'),
      dmc.Anchor('Editor', href='/editor', id='nav-editor'),
    ]),
    dmc.Group([
      theme_toggle,
    ]),
  ],
  align='center',
  justify='space-between',
  style={'flex': 1},
  h='100%',
  px='md',
)

@callback(
  Output('nav-viewer', 'aria-current'),
  Output('nav-editor', 'aria-current'),
  Input('url', 'pathname'),
)
def update_active_link(pathname):
  def active_if(pattern):
    if isinstance(pattern, (list, tuple)):
      return 'page' if any(re.fullmatch(p, pathname) for p in pattern) else ''
    return 'page' if re.fullmatch(pattern, pathname) else ''

  return active_if(['/', r'^/viewer$', r'^/viewer/.*$']), active_if([r'^/editor$', r'^/editor/.*$'])