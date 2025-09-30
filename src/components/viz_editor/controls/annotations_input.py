import json

import dash_mantine_components as dmc
from dash import ALL, Input, Output, State, callback, ctx, dcc

from src.components.chart import Annotation

# Simplified add annotation button
add_annotation_button = dmc.Button(
  'Add annotation',
  leftSection='➕',
  id='add-annotation-button',
  variant='light',
  size='sm',
)


def remove_annotation_button(index=0):
  return dmc.ActionIcon(
    '🗑️',
    variant='subtle',
    size='lg',
    id={'type': 'remove-annotation', 'index': index},
  )


def annotation_row(index, label='', value=0, color='#222222'):
  """Create a single annotation row with error handling."""
  try:
    return dmc.Group(
      [
        dmc.NumberInput(
          value=value,
          label='Value',
          placeholder='Enter y-value',
          id={'type': 'annotation-value', 'index': index},
          size='sm',
          w=85,
        ),
        dmc.TextInput(
          value=label,
          label='Label',
          placeholder='Label',
          id={'type': 'annotation-label', 'index': index},
          size='sm',
          style=dict(flex=1),
        ),
        dmc.ColorInput(
          id={'type': 'annotation-color', 'index': index},
          value=color,
          label='Color',
          w=105,
        ),
        remove_annotation_button(index),
      ],
      gap='xs',
      align='flex-end',
    )
  except Exception as e:
    print(f'Error creating annotation row {index}: {e}')
    return dmc.Text(f'Error creating annotation row {index}: {str(e)}', color='red')


def annotations_input(value=[]):
  """Create the annotations input component."""
  return dmc.Stack(
    id='annotations-input',
    children=[
      dcc.Store(id='annotations-store', storage_type='memory', data=value),
      dmc.Text('Annotations', size='sm'),
      dmc.Stack(
        id='annotations-container',
        children=[],
        gap='sm',
      ),
      add_annotation_button,
    ],
  )


@callback(
  Output('annotations-container', 'children'),
  Input('annotations-store', 'data'),
)
def render_annotations(data: list[dict]):
  """Render annotation rows based on store data."""
  if not data:
    return []

  try:
    annotations = [Annotation.from_dict(annotation_data) for annotation_data in data]
    rows = []
    for i, annotation in enumerate(annotations):
      try:
        row = annotation_row(
          index=i,
          label=annotation.label,
          value=annotation.value,
          color=annotation.color,
        )
        rows.append(row)
      except Exception as e:
        print(f'Error creating annotation row {i}: {e}')
        rows.append(dmc.Text(f'Error in annotation {i}: {str(e)}', color='red'))

    return rows
  except Exception as e:
    print(f'Error in render_annotations: {e}')
    return [dmc.Text(f'Error rendering annotations: {str(e)}', color='red')]


@callback(
  Output('annotations-store', 'data'),
  Input('add-annotation-button', 'n_clicks'),
  Input({'type': 'remove-annotation', 'index': ALL}, 'n_clicks'),
  Input({'type': 'annotation-value', 'index': ALL}, 'value'),
  Input({'type': 'annotation-label', 'index': ALL}, 'value'),
  Input({'type': 'annotation-color', 'index': ALL}, 'value'),
  State('annotations-store', 'data'),
  prevent_initial_call=True,
)
def update_annotations(
  add_clicks: int,
  remove_clicks: int,
  values: list[float],
  labels: list[str],
  colors: list[str],
  stored: list[dict],
):
  """Handle add/remove actions and field updates for annotations."""
  stored = stored or []

  # Get the trigger information
  trigger = ctx.triggered[0] if ctx.triggered else None

  if not trigger:
    return stored

  trigger_id = trigger['prop_id']

  # Handle add annotation button click
  if 'add-annotation-button' in trigger_id:
    stored.append(
      {
        'value': 0,
        'label': '',
        'color': '#00abc7',
      }
    )
    return stored

  # Handle remove annotation button click
  if 'remove-annotation' in trigger_id:
    # Extract index from trigger_id
    trigger_data = json.loads(trigger_id.split('.')[0])
    index = trigger_data['index']
    if 0 <= index < len(stored):
      stored.pop(index)
    return stored

  # Handle field updates (value, label, color changes)
  if any(x in trigger_id for x in ['annotation-value', 'annotation-label', 'annotation-color']):
    # Update the stored data with current field values
    for i in range(len(stored)):
      if i < len(values) and values[i] is not None:
        stored[i]['value'] = values[i]
      if i < len(labels) and labels[i] is not None:
        stored[i]['label'] = labels[i]
      if i < len(colors) and colors[i] is not None:
        stored[i]['color'] = colors[i]

  return stored
