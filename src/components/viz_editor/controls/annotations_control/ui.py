import dash_mantine_components as dmc
from dash_iconify import DashIconify
from datetime import datetime
from dash import dcc, html


def annotation_type_icon(
  orientation: str, size: int = 32, color: str = 'var(--mantine-color-dimmed)'
):
  """Return an inline SVG icon (raw HTML)."""
  margin = 3  # px
  if orientation == 'horizontal':
    path = f'M{margin},{size/2} L{size-margin},{size/2}'
  else:
    path = f'M{size/2},{margin} L{size/2},{size-margin}'
  svg = f"""
  <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
    <rect x="0" y="0" width="{size}" height="{size}" stroke="none" stroke-width="0" fill="#9992" rx="6" />
    <path d="{path}" stroke="{color}" stroke-width="3" fill="none" stroke-dasharray="5 2" />
  </svg>
  """
  return dcc.Markdown(svg, dangerously_allow_html=True, style=dict(height='32px', aspectRatio='1 / 1'))


def annotation_color_input(value='#222222'):
  return dmc.ColorInput(
    id='form-annotation-color',
    label='Color',
    value=value,
    format='hex',
  )


def annotation_type_select(value='horizontal'):
  return dmc.Select(
    data=[
      {'value': 'vertical', 'label': 'X'},
      {'value': 'horizontal', 'label': 'Y'},
    ],
    value=value,
    label='Axis',
    id='form-annotation-type',
    size='sm',
    w=60,
    allowDeselect=False,
  )


def annotation_value_input(annotation_type='horizontal', annotation_value=0):
  if annotation_type == 'vertical':
    return dmc.DatePickerInput(
      value=annotation_value,
      label='Date',
      id='form-annotation-value',
      size='sm',
      style=dict(flex=1),
    )
  return dmc.NumberInput(
    value=annotation_value,
    label='Value',
    id='form-annotation-value',
    size='sm',
    style=dict(flex=1),
  )


def annotation_label_input(value=''):
  return dmc.TextInput(
    value=value,
    label='Label',
    id='form-annotation-label',
    size='sm',
    style=dict(flex=1),
  )


def annotation_row(index, type, value, label, color):
  """Display a single annotation row with brief summary and edit/remove buttons."""

  # format value depending on type
  display_value = value
  if type == 'vertical' and value:
    # ensure value is a datetime object
    if isinstance(value, str):  # should be
      try:
        value_dt = datetime.fromisoformat(value)
      except ValueError:
        value_dt = None
    elif isinstance(value, datetime):
      value_dt = value
    else:
      value_dt = None

    if value_dt:
      display_value = value_dt.strftime('%B %-d, %Y')  # "October 31, 2025"

  if type == 'horizontal' and isinstance(value, (int, float)):
    display_value = f'{value:,}'

  return dmc.Flex(
    [
      annotation_type_icon(type, color=color),
      dmc.Stack(
        [
          dmc.Text(display_value, size='sm', fw=500),
          dmc.Text(
            label,
            size='xs',
            c='dimmed',
          ),
        ],
        gap=0,
        style=dict(overflow='hidden', textOverflow='ellipsis', whiteSpace='wrap', flex=1),
      ),
      dmc.ButtonGroup(
        [
          dmc.ActionIcon(
            DashIconify(icon='feather:edit-3'),
            id={'type': 'edit-annotation-button', 'index': index},
            variant='light',
          ),
          dmc.Space(w=8),
          dmc.ActionIcon(
            DashIconify(icon='feather:trash-2', color='crimson'),
            id={'type': 'remove-annotation-button', 'index': index},
            variant='light',
          ),
        ],
        className='annotation-actions',
      ),
    ],
    gap='xs',
    align='space-between',
    className='annotation-row',
  )
