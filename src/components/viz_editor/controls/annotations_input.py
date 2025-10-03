import dash_mantine_components as dmc
from dash import ALL, Input, Output, State, callback, ctx, dcc
from dash_iconify import DashIconify

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
    # size='lg',
    id={'type': 'remove-annotation', 'index': index},
  )


def color_picker_popover(index, value='#222222'):
  return dmc.Popover(
    position='bottom-start',
    withArrow=True,
    trapFocus=True,
    closeOnEscape=True,
    closeOnClickOutside=True,
    children=[
      dmc.PopoverTarget(
        dmc.ActionIcon(
          DashIconify(icon='feather:droplet', color=value),
          id={'type': 'color-button', 'index': index},
          variant='light',
          # size='lg',
        )
      ),
      dmc.PopoverDropdown(
        dmc.ColorPicker(
          id={'type': 'color-value', 'index': index},
          value=value,
          format='hex',
          swatches=[
            '#222222',
            '#663399',
            '#993366',
            '#ff0000',
            '#00abc7',
            '#00ff00',
            '#ff9900',
          ],
          fullWidth=True,
        ),
        style=dict(padding='0.5rem'),
      ),
    ],
  )


def annotation_row(index, axis, value=0, label='', color='#222222'):
  axis_selector = dmc.Select(
    data=[{'value': 'x', 'label': 'X'}, {'value': 'y', 'label': 'Y'}],
    value=axis,
    label='Axis',
    id={'type': 'annotation-axis', 'index': index},
    size='sm',
    w=60,
    allowDeselect=False,
  )

  # value input (date if x-axis, number if y-axis)
  if axis == 'x':
    value_input = dmc.DatePickerInput(
      value=value,  # datetime.date or string like '2025-10-01'
      label='Date',
      placeholder='Pick a date',
      id={'type': 'annotation-value', 'index': index},
      size='sm',
      w=145,
    )
  else:
    value_input = dmc.NumberInput(
      value=value,
      label='Value',
      placeholder='Enter y-value',
      id={'type': 'annotation-value', 'index': index},
      size='sm',
      w=145,
    )

  return dmc.Group(
    [
      axis_selector,
      value_input,
      dmc.TextInput(
        value=label,
        label='Label',
        placeholder='Label',
        id={'type': 'annotation-label', 'index': index},
        size='sm',
        style=dict(flex=1),
      ),
      color_picker_popover(index=index, value=color),
      remove_annotation_button(index),
    ],
    gap='xs',
    align='flex-end',
  )


def annotations_input(value=[]):
  """Create the annotations input component."""
  return dmc.Stack(
    id='annotations-input',
    children=[
      dcc.Store(id='annotations-store', storage_type='memory', data=value),
      dmc.Text('Annotations', size='md'),
      dmc.Divider(),
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
def render_annotations(data: list[dict] | None):
  """Render annotation rows based on store data."""
  if not data:
    return []
  return [
    annotation_row(
      index,
      d.get('axis'),
      d.get('value'),
      d.get('label'),
      d.get('color'),
    )
    for index, d in enumerate(data)
  ]


@callback(
  Output('annotations-store', 'data'),
  Input('add-annotation-button', 'n_clicks'),
  Input({'type': 'remove-annotation', 'index': ALL}, 'n_clicks'),
  Input({'type': 'annotation-axis', 'index': ALL}, 'value'),
  Input({'type': 'annotation-value', 'index': ALL}, 'value'),
  Input({'type': 'annotation-label', 'index': ALL}, 'value'),
  Input({'type': 'color-value', 'index': ALL}, 'value'),
  State('annotations-store', 'data'),
  prevent_initial_call=True,
)
def update_annotations(
  add_clicks: int,
  remove_clicks: int,
  axes: list[str],
  values: list[float],
  labels: list[str],
  colors: list[str],
  stored: list[dict],
):
  """Handle add/remove actions and field updates for annotations."""
  for i in range(len(stored)):
    stored[i]['axis'] = axes[i]
    stored[i]['label'] = labels[i]
    stored[i]['color'] = colors[i]
    stored[i]['value'] = values[i]

  # Get the trigger information
  trigger = ctx.triggered_id if ctx.triggered_id else None

  if not trigger:
    return stored

  # add new annotation
  if trigger == 'add-annotation-button':
    axis = 'y'
    stored.append(dict(axis=axis, value=None, label='', color='#00abc7', type='horizontal'))
    return stored
  # delete annotation
  elif isinstance(trigger, dict) and trigger.get('type') == 'remove-annotation':
    idx_to_remove = trigger['index']
    if 0 <= idx_to_remove < len(stored):
      stored.pop(idx_to_remove)

  return stored
