from dash import register_page, callback, Input, Output, html, dcc
import dash_mantine_components as dmc

from src.components.disclaimer import disclaimer
from src.components.round_summary import round_summary


register_page(__name__, path='/')


layout = dmc.Container(
  [
    dmc.Container(id='round-summary-container', children=round_summary(19)),
    dmc.Divider(my=48),
    disclaimer,
  ],
)

@callback(
  Output('round-summary-container', 'children'),
  Input('selected-round-store', 'data'),
)
def update_round_summary(selected_round):
  try:
    return round_summary(int(selected_round))
  except Exception:
    return dmc.Text('No round selected or invalid round.', color='red')
