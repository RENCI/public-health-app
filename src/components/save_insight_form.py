import datetime
import uuid
from typing import Any

import dash_mantine_components as dmc
from dash import Input, Output, State, callback, exceptions
from dash_iconify import DashIconify

default_control_values = {
  'theme': 'light',
  'plot_type': 'line',
  'round_num': 19,
  'pathogen': 'covid',
  'scenario_ids': [77, 78],
  'scenario_variables': [
    {
      'name': 'Vaccination Strategy',
      'options': ['High risk', 'All ages'],
      'selected_option': 'All ages',
    }
  ],
  'model_names': ['Ensemble'],
  'location_name': 'US',
  'target': 'incident_hospitalization',
  'age_group': '0-130',
  'x_axis': 'target_end_date',
  'y_axis': 'value',
  'x_start_date': '2025-01-01',
  'zoom': None,
}

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


@callback(
  Output('custom-insights-store', 'data', allow_duplicate=True),
  Output('insight-title-input', 'error'),
  Output('insight-description-input', 'error'),
  Output('notification-container', 'sendNotifications', allow_duplicate=True),
  Output('_pages_location', 'pathname'),  # update path
  Input('save-insight-button', 'n_clicks'),
  State('custom-insights-store', 'data'),
  State('insight-title-input', 'value'),
  State('insight-description-input', 'value'),
  State('selected-round-store', 'data'),
  State('chart-controls-store', 'data'),
  suppress_callback_exceptions=True,
  prevent_initial_call=True,
)
def save_custom_insight(
  n_clicks: int,
  current_custom_insights: list[dict[str, Any]],
  title: str,
  description: str,
  round_number: str,
  current_chart_controls: dict[str, Any] | None = None,
):
  if not n_clicks:
    raise exceptions.PreventUpdate

  # validation
  if not (title and title.strip() and description and description.strip()):
    raise exceptions.PreventUpdate

  now = datetime.datetime.now(datetime.timezone.utc).isoformat()
  new_id = f'custom-{uuid.uuid4()}'
  new_item = dict(
    id=new_id,
    title=title.strip(),
    description=description.strip(),
    image_url='https://placehold.co/400?text=Visualization',
    created_at=now,
    updated_at=now,
    controls={
      'round': round_number,
      **default_control_values,
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
    None,
    [notification],
    f'/insight/{new_id}',
  )
