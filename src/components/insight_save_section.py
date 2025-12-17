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


def insight_save_section():
  """
  Inline Save + Confirm section
  """
  return dmc.Stack(
    [
      dcc.Store(id='thumbnail-store'),

      dmc.Text(
        'This insight will be saved to your custom insights and will show in your Custom Insights list on the Round Summary page.',
        size='sm',
      ),
      dmc.Text(
        'You will be redirected to view this saved insight after confirmation.',
        size='sm',
        c='dimmed',
      ),

      dmc.Text(
        id='insight-save-helper-text',
        size='sm',
        c='red',
      ),

      # primary save button (`idle` state)
      toolbar_button(
        'Save',
        icon=DashIconify(icon='feather:save'),
        id='insight-save-button',
        color='blue',
        size='lg',
        w='50%',
        h='4rem',
        m='2rem auto',
        style={'display': 'block'},
      ),

      # confirmation button (`armed` state)
      toolbar_button(
        'Confirm Save',
        icon=DashIconify(icon='feather:check'),
        id='insight-save-confirm-button',
        color='red',
        size='lg',
        w='50%',
        h='4rem',
        m='2rem auto',
        style={'display': 'none'},
      ),
    ],
    gap='xs',
  )


# button visibility / confirmation flow
@callback(
  Output('insight-save-button', 'style'),
  Output('insight-save-confirm-button', 'style'),
  Output('insight-save-helper-text', 'children'),
  Input('insight-save-button', 'n_clicks'),
  Input('insight-save-confirm-button', 'n_clicks'),
  prevent_initial_call=True,
)
def toggle_save_buttons(save_clicks, confirm_clicks):
  trigger = ctx.triggered_id

  # first click: arm confirmation
  if trigger == 'insight-save-button':
    return (
      {'display': 'none'},
      {'display': 'block'},
      'Click again to confirm saving this insight.',
    )

  # confirm click (or fallback): reset UI
  return (
    {'display': 'block'},
    {'display': 'none'},
    '',
  )


# thumbnail capture, fires on confirm
clientside_callback(
  'window.dash_clientside.clientside.capture_thumbnail',
  Output('thumbnail-store', 'data'),
  Input('insight-save-confirm-button', 'n_clicks'),
  prevent_initial_call=True,
)


# save, in response to thumbnail capture.
# bc we want to use that thumbnail _in_ the saved insight,
# we do the thumbnail-generation first (above),
# then its completion triggers the save logic.
@callback(
  Output('custom-insights-store', 'data', allow_duplicate=True),
  Output('insight-title-input', 'error'),
  Output('notification-container', 'sendNotifications', allow_duplicate=True),
  Output('_pages_location', 'pathname'),
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
  )
