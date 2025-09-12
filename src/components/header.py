import re

import dash_mantine_components as dmc
from dash import Input, Output, callback, dcc

from .theme_toggle import theme_toggle

logo = dcc.Link(
  dmc.Image(src='/assets/images/covid19-smh-logo.png', alt='SMH Logo'),
  style=dict(width='275px'),
  href='/',
)

header = dmc.Flex(
  children=[
    dmc.Group(
      [
        logo,
        dmc.Anchor('Viewer', href='/', id='nav-viewer', style=dict(paddingTop='1rem')),
        dmc.Anchor('Explorer', href='/explorer', id='nav-explorer', style=dict(paddingTop='1rem')),
      ],
    ),
    dmc.Group(
      [
        theme_toggle,
      ]
    ),
  ],
  align='stretch',
  justify='space-between',
  style={'flex': 1},
  h='100%',
  px='md',
  py=0,
)


@callback(
  Output('nav-viewer', 'aria-current'),
  Output('nav-explorer', 'aria-current'),
  Input('url', 'pathname'),
)
def update_active_link(pathname):
  def active_if(pattern):
    if isinstance(pattern, (list, tuple)):
      return 'page' if any(re.fullmatch(p, pathname) for p in pattern) else ''
    return 'page' if re.fullmatch(pattern, pathname) else ''

  return active_if(['/', r'^/viewer$', r'^/viewer/.*$']), active_if(
    [r'^/explorer$', r'^/explorer/.*$']
  )
