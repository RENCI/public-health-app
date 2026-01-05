import datetime
import uuid
from typing import Any

import dash_mantine_components as dmc
from dash import (
  Input,
  Output,
  State,
  callback,
  clientside_callback,
  ctx,
  dcc,
  exceptions,
)
from dash_iconify import DashIconify

from src.components.toolbar import toolbar_button

from src.util.constants import DEFAULT_CONTROL_VALUES


def insight_save_modal():
  return dmc.Modal(
    children=[
      dmc.Text(
        'This insight will be saved to your custom insights and will show in your Custom Insights list on the Round Summary page.'
      ),
      dmc.Space(h=16),
      dmc.Text('You will be redirected to view this saved insight after confirmation.'),
      dmc.Space(h=16),
      dmc.Text('Are you sure you want to save this insight?', fw='bold'),
      dmc.Text(''),
      dmc.Group(
        [
          dmc.Button('Cancel', id='insight-save-cancel-button', variant='outline', color='red.5'),
          dmc.Button('Confirm Save', id='insight-save-confirm-button', color='blue'),
        ],
        justify='flex-end',
        mt='md',
      ),
      dcc.Store(id='thumbnail-store'),
    ],
    title='Save Custom Insight',
    id='insight-save-modal',
    opened=False,
    size='lg',
  )


def insight_save_modal_button():
  return toolbar_button(
    'SAVE',
    icon=DashIconify(icon='feather:save'),
    id='insight-save-modal-button',
    color='blue',
    size='lg',
    w='50%',
    h='4rem',
    m='2rem auto',
  )


@callback(
  Output('insight-save-modal', 'opened'),
  Input('insight-save-modal-button', 'n_clicks'),
  Input('insight-save-confirm-button', 'n_clicks'),
  Input('insight-save-cancel-button', 'n_clicks'),
  prevent_initial_call=True,
)
def show_modal(open_click, confirm_click, cancel_click):
  if not ctx.triggered_id:
    # shouldn't happen, but safe fallback
    return False

  trigger = ctx.triggered_id

  if trigger == 'insight-save-modal-button':
    return True  # open modal

  # both confirm + cancel close the modal
  if trigger in ('insight-save-confirm-button', 'insight-save-cancel-button'):
    return False

  return False


clientside_callback(
  'window.dash_clientside.clientside.capture_thumbnail',
  Output('thumbnail-store', 'data'),
  Input('insight-save-confirm-button', 'n_clicks'),
)


@callback(
  Output('custom-insights-store', 'data', allow_duplicate=True),
  Output('insight-title-input', 'error'),
  Output('notification-container', 'sendNotifications', allow_duplicate=True),
  Output('_pages_location', 'pathname'),  # update path
  Output('insight-save-modal', 'opened', allow_duplicate=True),
  Input('thumbnail-store', 'data'),
  State('custom-insights-store', 'data'),
  State('insight-title-input', 'value'),
  State({'type': 'editor', 'id': 'insight-summary-input'}, 'value'),
  State({'type': 'editor', 'id': 'insight-discussion-input'}, 'value'),
  State('selected-round-store', 'data'),
  State('chart-controls-store', 'data'),
  suppress_callback_exceptions=True,
  prevent_initial_call=True,
)
def save_custom_insight(
  thumbnail_data,
  current_custom_insights: list[dict[str, Any]],
  title: str,
  summary: str,
  description: str,
  round_number: str,
  current_chart_controls: dict[str, Any] | None = None,
):
  # validation
  if not (thumbnail_data and title and title.strip() and description and description.strip()):
    raise exceptions.PreventUpdate

  now = datetime.datetime.now(datetime.timezone.utc).isoformat()
  new_id = f'custom-{uuid.uuid4()}'
  image_url = thumbnail_data or 'https://placehold.co/400?text=Visualization'
  new_item = dict(
    id=new_id,
    title=title.strip(),
    summary=summary.strip(),
    description=description.strip(),
    image_url=image_url,
    created_at=now,
    updated_at=now,
    controls={
      'round': round_number,
      **DEFAULT_CONTROL_VALUES,
      **(current_chart_controls or {}),
    },
  )

  notification = {
    'action': 'show',
    'id': f'save-success-{uuid.uuid4()}',
    'message': f'Insight "{title.strip()}" saved successfully!',
    'color': 'limegreen',
  }

  current_custom_insights = current_custom_insights or []
  return (
    current_custom_insights + [new_item],
    None,
    [notification],
    f'/insight/{new_id}',
    False,
  )
