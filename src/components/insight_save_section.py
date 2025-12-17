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
  return dmc.Card(
    dmc.Stack(
      [
        dcc.Store(id='thumbnail-store'),
        dmc.Text(
          'Saving this insight will add it to your Custom Insights list on the Round Summary page.',
          size='sm',
          w='90%',
          ta='center',
          m='auto',
        ),
        dmc.Text(
          'You will be redirected to view your newly saved insight upon confirmation.',
          size='sm',
          w='90%',
          ta='center',
          m='auto',
          c='dimmed',
        ),
        dmc.Text(
          id='insight-save-helper-text',
          size='sm',
          c='lime',
          ta='center',
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
          m='var(--mantine-spacing-sm) auto',
          style=dict(display='block'),
        ),
        # confirmation button (`armed` state)
        toolbar_button(
          'Confirm Save',
          icon=DashIconify(icon='feather:check'),
          id='insight-save-confirm-button',
          color='lime',
          size='lg',
          w='50%',
          h='4rem',
          m='var(--mantine-spacing-sm) auto',
          style=dict(display='none'),
        ),
        dcc.Interval(
          id='confirm-timeout',
          interval=5_000,
          n_intervals=0,
          disabled=True
        )
      ],
      gap='xs',
    )
  )


@callback(
  Output('confirm-timeout', 'disabled'),
  Input('insight-save-button', 'n_clicks'),
  Input('insight-save-confirm-button', 'n_clicks'),
prevent_initial_call=True,
)
def toggle_timeout(save_clicks, confirm_clicks):
  trigger = ctx.triggered_id
  # Enable interval only when save button is clicked to arm confirmation
  return trigger != 'insight-save-button'

# button visibility / confirmation flow
@callback(
  Output('insight-save-button', 'style'),
  Output('insight-save-confirm-button', 'style'),
  Output('insight-save-helper-text', 'children'),
  Input('insight-save-button', 'n_clicks'),
  Input('insight-save-confirm-button', 'n_clicks'),
  Input('confirm-timeout', 'n_intervals'),
  prevent_initial_call=True,
)
def toggle_save_buttons(save_clicks, confirm_clicks, timout_intervals):
  trigger = ctx.triggered_id

  # first click: arm confirmation
  if trigger == 'insight-save-button':
    return (
      {'display': 'none'},
      {'display': 'block'},
      'Click again to confirm saving this insight.',
    )

  # confirm click or timeout (or fallback): reset UI
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
