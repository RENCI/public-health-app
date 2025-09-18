
import dash_mantine_components as dmc
from dash import (
  register_page,
)

from src.components.disclaimer import disclaimer
from src.components.round_report import round_report


from ..util.data import load_rounds

rounds = load_rounds()
print(rounds)

register_page(__name__, path='/')


def tipped_text(text, tooltip=None, size='md'):
  return dmc.Tooltip(
    label=tooltip if tooltip else text,
    position='top',
    withArrow=True,
    children=dmc.Text(text, size=size, c='gray'),
  )

layout = dmc.Container(
  [
    round_report(19),
    dmc.Divider(my=48),
    disclaimer,
  ],
)
