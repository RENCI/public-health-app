import datetime
import uuid
from typing import Any

import dash_mantine_components as dmc
from dash import Input, Output, State, callback, clientside_callback, dcc, exceptions
from dash_iconify import DashIconify

from src.components.chart import DEFAULT_CONTROL_VALUES, Chart

form_toggle_button = dmc.Button(
  'Save as New Insight',
  leftSection=DashIconify(icon='feather:save'),
  id='reveal-form-button',
  style=dict(alignSelf='center'),
)


def save_insight_form(initial_title='', initial_description=''):
  return dmc.Stack(
    [
      form_toggle_button,
      dmc.Collapse(
        id='save-form-container',
        opened=False,
        children=[
          dmc.Card(
            children=[
              dmc.Stack(
                [
                  dmc.TextInput(
                    id='insight-title-input',
                    value=initial_title,
                    label='Title',
                  ),
                  dmc.Textarea(
                    id='insight-description-input',
                    value=initial_description,
                    label='Description',
                    autosize=True,
                    minRows=5,
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
                    id='hide-form-button',
                  ),
                  dmc.Button(
                    'Save',
                    leftSection=DashIconify(icon='feather:check'),
                    id='save-insight-button',
                  ),
                ],
                justify='flex-end',
              ),
            ]
          )
        ],
      ),
      dcc.Store(id='thumbnail-store'),
    ]
  )


@callback(
  Output('save-form-container', 'opened'),
  Input('reveal-form-button', 'n_clicks'),
  Input('hide-form-button', 'n_clicks'),
  State('save-form-container', 'opened'),
  prevent_initial_call=True,
)
def toggle_form_visibility(reveal_clicks, hide_clicks, is_visible):
  return not is_visible


clientside_callback(
  'window.dash_clientside.clientside.capture_thumbnail',
  Output('thumbnail-store', 'data'),
  Input('save-insight-button', 'n_clicks'),
)


@callback(
  Output('custom-insights-store', 'data', allow_duplicate=True),
  Output('insight-title-input', 'error'),
  Output('insight-description-input', 'error'),
  Output('notification-container', 'sendNotifications', allow_duplicate=True),
  Output('_pages_location', 'pathname'),  # update path
  Input('thumbnail-store', 'data'),
  State('custom-insights-store', 'data'),
  State('insight-title-input', 'value'),
  State('insight-description-input', 'value'),
  State('selected-round-store', 'data'),
  State('chart-controls-store', 'data'),
  State('graph', 'relayoutData'),
  suppress_callback_exceptions=True,
  prevent_initial_call=True,
)
def save_custom_insight(
  thumbnail_data,
  current_custom_insights: list[dict[str, Any]],
  title: str,
  description: str,
  round_number: str,
  current_chart_controls: dict[str, Any] | None = None,
  relayout_data: dict[str, Any] | None = None,
):
  # validation
  if not (title and title.strip() and description and description.strip()):
    raise exceptions.PreventUpdate

  now = datetime.datetime.now(datetime.timezone.utc).isoformat()
  new_id = f'custom-{uuid.uuid4()}'
  image_url = thumbnail_data or 'https://placehold.co/400?text=Visualization'

  # Save chart controls with round number
  controls_to_save = {
    **DEFAULT_CONTROL_VALUES,
    'round': round_number,
    **(current_chart_controls or {}),
  }
  # Override chart controls zoom with current zoom from relayout data
  if relayout_data:
    current_zoom = Chart.calculate_zoom_from_relayout(relayout_data)
    if current_zoom:
      controls_to_save['zoom'] = current_zoom.to_dict()

  new_item = dict(
    id=new_id,
    title=title.strip(),
    description=description.strip(),
    image_url=image_url,
    created_at=now,
    updated_at=now,
    controls=controls_to_save,
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
    None,
    [notification],
    f'/insight/{new_id}',
  )
