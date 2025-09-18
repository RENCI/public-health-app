import uuid

import dash_mantine_components as dmc
from dash import (
  ALL,
  Input,
  Output,
  State,
  callback,
  ctx,
  dcc,
  exceptions,
  no_update,
  register_page,
)
from dash_iconify import DashIconify

from src.components.disclaimer import disclaimer
from src.components.round_report import round_report

from src.util.format_timestamp import format_timestamp
from src.util.time_ago import time_ago

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


@callback(
  Output('delete-confirmation-modal', 'opened', allow_duplicate=True),
  Output('delete-confirmation-modal', 'data', allow_duplicate=True),
  Output('custom-insights-store', 'data', allow_duplicate=True),
  Output('notification-container', 'sendNotifications', allow_duplicate=True),
  Input({'type': 'delete-insight', 'id': ALL}, 'n_clicks'),
  Input('cancel-delete', 'n_clicks'),
  Input('confirm-delete', 'n_clicks'),
  State('delete-confirmation-modal', 'data'),
  State('custom-insights-store', 'data'),
  prevent_initial_call=True,
)
def handle_delete(delete_clicks, cancel_click, confirm_click, modal_data, custom_insights):
  triggered = ctx.triggered_id

  # defaults
  # opened, data, updated_store, notifications = False, no_update, no_update, no_update

  # Case 1: delete button clicked → open modal
  if isinstance(triggered, dict) and triggered.get('type') == 'delete-insight':
    if not any(delete_clicks):
      raise exceptions.PreventUpdate
    return True, triggered['id'], no_update, no_update

  # Case 2: cancel → just close modal
  if triggered == 'cancel-delete':
    return False, no_update, no_update, no_update

  # Case 3: confirm → actually delete
  if triggered == 'confirm-delete' and modal_data:
    insight_id = modal_data
    if not custom_insights:
      raise exceptions.PreventUpdate

    deleted = next((ci for ci in custom_insights if ci['id'] == insight_id), None)
    updated = [ci for ci in custom_insights if ci['id'] != insight_id]

    notification = {
      'action': 'show',
      'id': f'delete-success-{uuid.uuid4()}',
      'message': f'Insight "{deleted["title"].strip()}" deleted successfully!'
      if deleted
      else 'Insight deleted.',
      'color': 'green',
    }

    return False, no_update, updated, [notification]

  raise exceptions.PreventUpdate
