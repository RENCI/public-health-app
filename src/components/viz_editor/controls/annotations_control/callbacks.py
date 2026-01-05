from datetime import datetime

from dash import ALL, Input, Output, State, callback, ctx, exceptions
import dash_mantine_components as dmc

from .store import remove_annotation
from .ui import (
  annotation_color_input,
  annotation_label_input,
  annotation_row,
  annotation_type_select,
  annotation_value_input,
)


@callback(
  Output('annotations-container', 'children'),
  Input('annotations-store', 'data'),
)
def render_annotations(data):
  if not data:
    return [
      dmc.Text(
        ['No annotations exist for this insight yet.'],
        ta='center',
        size='sm',
        c='dimmed',
        my='md',
      )
    ]
  return [
    annotation_row(i, d['type'], d['value'], d['label'], d['color']) for i, d in enumerate(data)
  ]


# --- Modal logic (open/close) ---------------------------------------------


@callback(
  Output('annotation-modal', 'opened', allow_duplicate=True),
  Output('edit-index-store', 'data'),
  Input('add-annotation-button', 'n_clicks'),
  Input({'type': 'edit-annotation-button', 'index': ALL}, 'n_clicks'),
  Input('cancel-edit-annotation-button', 'n_clicks'),
  Input('confirm-edit-annotation-button', 'n_clicks'),
  State('annotations-store', 'data'),
  prevent_initial_call=True,
)
def handle_edit_modal(add_clicks, edit_clicks, cancel_clicks, confirm_clicks, store):
  if ctx.triggered_id is None or ctx.triggered[0]['value'] in [None, 0]:
    raise exceptions.PreventUpdate

  trigger = ctx.triggered_id
  store = store or []

  if trigger == 'cancel-edit-annotation-button':
    return False, None

  if trigger == 'confirm-edit-annotation-button':
    return False, None

  if trigger == 'add-annotation-button':
    return True, len(store)

  if isinstance(trigger, dict) and trigger.get('type') == 'edit-annotation-button':
    return True, trigger.get('index')

  raise exceptions.PreventUpdate


@callback(
  Output('remove-annotation-modal', 'opened'),
  Output('edit-index-store', 'data', allow_duplicate=True),
  Input({'type': 'remove-annotation-button', 'index': ALL}, 'n_clicks'),
  Input('cancel-remove-annotation-button', 'n_clicks'),
  Input('confirm-remove-annotation-button', 'n_clicks'),
  State('annotations-store', 'data'),
  prevent_initial_call=True,
)
def handle_remove_annotation_modal(remove_clicks, cancel_clicks, confirm_clicks, store):
  if ctx.triggered_id is None or ctx.triggered[0]['value'] in [None, 0]:
    raise exceptions.PreventUpdate

  trigger = ctx.triggered_id
  store = store or []

  if trigger == 'cancel-remove-annotation-button':
    return False, None

  if trigger == 'confirm-remove-annotation-button':
    return False, None

  if isinstance(trigger, dict) and trigger.get('type') == 'remove-annotation-button':
    remove_index = trigger.get('index')
    if 0 <= remove_index < len(store):
      return True, remove_index

  raise exceptions.PreventUpdate


# --- Store synchronization ------------------------------------------------


@callback(
  Output('annotations-store', 'data'),
  Input('confirm-edit-annotation-button', 'n_clicks'),
  Input('confirm-remove-annotation-button', 'n_clicks'),
  State('form-annotation-type', 'value'),
  State('form-annotation-value', 'value'),
  State('form-annotation-label', 'value'),
  State('form-annotation-color', 'value'),
  State('annotations-store', 'data'),
  State('edit-index-store', 'data'),
  prevent_initial_call=True,
)
def sync_annotations(_, __, type, value, label, color, store, edit_index):
  trigger = ctx.triggered_id
  store = store or []

  if trigger == 'confirm-edit-annotation-button':
    if edit_index is None or edit_index < 0:
      raise exceptions.PreventUpdate
    else:
      if edit_index < len(store):
        store[edit_index]['type'] = type
        store[edit_index]['value'] = value
        store[edit_index]['label'] = label
        store[edit_index]['color'] = color
      elif edit_index == len(store):
        store.append(dict(type=type, value=value, label=label, color=color))
    return store

  if trigger == 'confirm-remove-annotation-button':
    return remove_annotation(store, edit_index)

  raise exceptions.PreventUpdate


# --- Form population ------------------------------------------------------


@callback(
  Output('annotation-form-container', 'children'),
  Input('edit-index-store', 'data'),
  Input('form-annotation-type', 'value'),
  Input('form-annotation-value', 'value'),
  Input('form-annotation-label', 'value'),
  Input('form-annotation-color', 'value'),
  State('annotations-store', 'data'),
  prevent_initial_call=True,
)
def populate_annotation_form(
  edit_index, annotation_type, annotation_value, annotation_label, annotation_color, store
):
  trigger = ctx.triggered_id
  store = store or []

  if edit_index is None or edit_index < 0:
    raise exceptions.PreventUpdate

  if trigger == 'edit-index-store':
    if edit_index < len(store):
      current = store[edit_index]
      annotation_type = current.get('type')
      annotation_value = current.get('value')
      annotation_label = current.get('label')
      annotation_color = current.get('color')
    else:
      annotation_type = 'horizontal'
      annotation_value = 0
      annotation_label = ''
      annotation_color = '#222222'

  if trigger == 'form-annotation-type':
    annotation_value = 0 if annotation_type == 'horizontal' else datetime.now().strftime('%Y-%m-%d')

  return [
    annotation_type_select(annotation_type),
    annotation_value_input(annotation_type, annotation_value),
    annotation_label_input(annotation_label),
    annotation_color_input(annotation_color),
  ]
