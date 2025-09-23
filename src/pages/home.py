from dash import register_page
import dash_mantine_components as dmc

from src.components.disclaimer import disclaimer
from src.components.round_summary import round_summary


register_page(__name__, path='/')


layout = dmc.Container(
  [
    round_summary(),
    dmc.Divider(my=48),
    disclaimer,
  ],
)
