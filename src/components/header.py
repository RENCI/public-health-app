import re

import dash_mantine_components as dmc
from dash import Input, Output, callback, dcc

from .round_select import round_select
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
        round_select(),
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
