import datetime
import uuid

import dash_mantine_components as dmc
from dash import Input, Output, State, callback, exceptions, no_update
from dash_iconify import DashIconify

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
                    id='save-button',
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
  Output('custom-insights-store', 'data'),
  Output('insight-title-input', 'error'),
  Output('insight-description-input', 'error'),
  Output('notification-container', 'sendNotifications', allow_duplicate=True),
  Output('_pages_location', 'pathname'),  # update path
  Output('_pages_location', 'search'),  # add ?id=insight_id
  Input('save-button', 'n_clicks'),
  State('custom-insights-store', 'data'),
  State('insight-title-input', 'value'),
  State('insight-description-input', 'value'),
  State('selected-round-store', 'data'),
  State('scenarios-select', 'value'),
  State('models-select', 'value'),
  State('location-select', 'value'),
  State('target-select', 'value'),
  State('age-group-select', 'value'),
  State('uncertainty-select', 'value'),
  State('ensemble-select', 'value'),
  State('zoom-store', 'data'),
  State('annotations-store', 'data'),
  suppress_callback_exceptions=True,
  prevent_initial_call=True,
)
def save_custom_insight(
  n_clicks,
  current_store,
  title,
  description,
  round_number,
  scenarios,
  models,
  location,
  target,
  age_group,
  uncertainty,
  ensemble,
  zoom,
  annotations,
):
  if not n_clicks:
    raise exceptions.PreventUpdate

  # validation
  title_error = None
  desc_error = None
  if not title or not title.strip():
    title_error = 'Title is required.'
  if not description or not description.strip():
    desc_error = 'Description is required.'

  if title_error or desc_error:
    return no_update, title_error, desc_error, no_update, no_update, no_update

  now = datetime.datetime.utcnow().isoformat()
  new_id = f'custom-{uuid.uuid4()}'
  new_item = dict(
    id=new_id,
    title=title.strip(),
    description=description.strip(),
    image_url='https://placehold.co/400?text=Visualization',
    created_at=now,
    updated_at=now,
    controls=dict(
      round=round_number,
      scenarios=scenarios,
      models=models,
      location=location,
      target=target,
      age_group=age_group,
      uncertainty=uncertainty,
      ensemble=ensemble,
      zoom=zoom,
      annotations=annotations,
    ),
  )

  notification = {
    'action': 'show',
    'id': f'save-success-{uuid.uuid4()}',
    'message': f'Insight "{title.strip()}" saved successfully!',
    'color': 'limegreen',
  }

  current_store = current_store or []
  return (
    current_store + [new_item],
    None,
    None,
    [notification],
    '/insight',
    f'?id={new_id}',
  )
