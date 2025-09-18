
import dash_mantine_components as dmc
from dash import (
  register_page,
)

from src.components.disclaimer import disclaimer
from src.components.round_report import round_report


register_page(__name__, path='/')

layout = dmc.Container(
  [
    round_report(19),
    dmc.Divider(my=48),
    disclaimer,
  ],
)
