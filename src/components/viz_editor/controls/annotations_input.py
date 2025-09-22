import dash_mantine_components as dmc
from dash import ALL, Input, Output, State, callback, ctx, dcc
from dash_iconify import DashIconify

add_annotation_button = dmc.Button(
  'Add annotation',
  leftSection=DashIconify(icon='feather:plus'),
  id='add-annotation-button',
  variant='light',
  size='sm',
)


def remove_annotation_button(index=0):
  return dmc.ActionIcon(
    DashIconify(icon='feather:trash-2', color='crimson'),
    variant='subtle',
    size='lg',
    id={'type': 'remove-annotation', 'index': index},
  )


def annotation_row(index, label='', value=0, color='#222222'):
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
        id={'type': 'color-value', 'index': index},
        value=color,
        label='Color',
        w=105,
      ),
      remove_annotation_button(index),
    ],
    gap='xs',
    align='flex-end',
  )


def annotations_input(value=[]):
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


@callback(Output('annotations-container', 'children'), Input('annotations-store', 'data'))
def render_annotations(data):
  if not data:
    return []
  return [
    annotation_row(i, d.get('label'), d.get('value'), d.get('color')) for i, d in enumerate(data)
  ]


@callback(
  Output('annotations-store', 'data'),
  Input('add-annotation-button', 'n_clicks'),
  Input({'type': 'annotation-value', 'index': ALL}, 'value'),
  Input({'type': 'annotation-label', 'index': ALL}, 'value'),
  Input({'type': 'color-value', 'index': ALL}, 'value'),
  Input({'type': 'remove-annotation', 'index': ALL}, 'n_clicks'),
  State('annotations-store', 'data'),
  prevent_initial_call=True,
)
def manage_annotations(add_clicks, values, labels, colors, delete_clicks, stored):
  stored = stored or []

  # Update existing annotations from input fields
  if values is not None and labels is not None and colors is not None:
    for i in range(min(len(stored), len(values), len(colors))):
      stored[i]['value'] = values[i]
      stored[i]['label'] = labels[i]
      stored[i]['color'] = colors[i]

  trigger = ctx.triggered_id

  # add new annotation
  if trigger == 'add-annotation-button':
    stored.append(dict(value=None, label='', color='#00abc7'))

  # delete annotation
  elif isinstance(trigger, dict) and trigger.get('type') == 'remove-annotation':
    idx_to_remove = trigger['index']
    if 0 <= idx_to_remove < len(stored):
      stored.pop(idx_to_remove)

  return stored
