import datetime
import os
import uuid
import yaml
from typing import Any

import dash_mantine_components as dmc
from dash import (
  Input,
  Output,
  State,
  callback,
  callback_context,
  clientside_callback,
  dcc,
  exceptions,
)
from dash_iconify import DashIconify

from src.components.markdown_editor import markdown_editor
from src.components.toolbar import toolbar_button
from src.util.constants import DEFAULT_CONTROL_VALUES


# to use:
#   import insight_save_drawer and insight_save_drawer_button.
#   ensure both are in the layout.
#   pass insight dict into insight_yaml_modal.


def insight_save_drawer(
  initial_title='',
  initial_summary='',
  initial_description='',
):
  return dmc.Drawer(
    [
      dcc.Store(id='thumbnail-store'),
      dmc.Stack(
        [
          dmc.TextInput(
            id='insight-title-input',
            value=initial_title,
            label=dmc.Text('Title', c='blue', fz='lg'),
            size='lg',
            inputProps=dict(className='insight-form-input'),
            variant='filled',
          ),
          markdown_editor(
            editor_id='insight-summary-input',
            label='Summary',
            initial_value=initial_summary,
          ),
          markdown_editor(
            editor_id='insight-description-input',
            label='Description',
            initial_value=initial_description,
            min_height='300px',
          ),
        ],
        gap=24,
      ),
      dmc.Divider(my=24),
      dmc.Group(
        [
          dmc.Button(
            'Cancel',
            leftSection=DashIconify(icon='feather:x'),
            color='crimson',
            variant='outline',
            id='cancel-save-button',
          ),
          dmc.Button(
            'Save',
            leftSection=DashIconify(icon='feather:check'),
            id='save-insight-button',
          ),
        ],
        justify='flex-end',
      ),
    ],
    title='Save Insight',
    id='insight-save-modal',
    opened=False,
    position='bottom',
    size='lg',
    lockScroll=False,
    style=dict(minHeight='25vh'),
    overlayProps={
      'style': dict(display='none'),
    },
  )


def insight_save_drawer_button():
  return toolbar_button(
    'Save',
    icon=DashIconify(icon='feather:save'),
    id='insight-save-modal-button',
    variant='solid',
  )


@callback(
  Output('insight-save-modal', 'opened'),
  Input('insight-save-modal-button', 'n_clicks'),
  Input('cancel-save-button', 'n_clicks'),
  State('insight-save-modal', 'opened'),
  prevent_initial_call=True,
)
def toggle_modal(show_clicks, hide_clicks, opened):
  ctx = callback_context
  if not ctx.triggered:
    return opened
  button_id = ctx.triggered[0]['prop_id'].split('.')[0]
  if button_id == 'insight-save-modal-button':
    return True
  elif button_id == 'cancel-save-button':
    return False
  return opened


clientside_callback(
  'window.dash_clientside.clientside.capture_thumbnail',
  Output('thumbnail-store', 'data'),
  Input('save-insight-button', 'n_clicks'),
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
  State({'type': 'editor', 'id': 'insight-description-input'}, 'value'),
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
