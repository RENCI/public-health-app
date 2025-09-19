from dash import register_page, callback, Input, Output, html, dcc
import dash_mantine_components as dmc

from src.components.disclaimer import disclaimer
from src.components.round_report import round_report


register_page(__name__, path='/')


layout = dmc.Container(
  [
    dcc.Store(id='selected-round-store', data='19'),
    dmc.Container(id='round-report-container', children=round_report(19)),
    dmc.Divider(my=48),
    disclaimer,
  ],
)

@callback(
  Output('round-report-container', 'children'),
  Input('selected-round-store', 'data'),
)
def update_round_report(selected_round):
  try:
    return round_report(int(selected_round))
  except Exception:
    return dmc.Text('No round selected or invalid round.', color='red')
