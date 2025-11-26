import dash_mantine_components as dmc
from dash import dcc
from dash_iconify import DashIconify

from .callbacks import (
  handle_edit_modal,
  handle_remove_annotation_modal,
  populate_annotation_form,
  render_annotations,
  sync_annotations,
)
from .modals import (
  edit_annotation_modal,
  remove_annotation_modal,
)

add_annotation_button = dmc.Button(
  'Add annotation',
  leftSection=DashIconify(icon='feather:plus'),
  id='add-annotation-button',
  variant='light',
  size='sm',
)


def annotations_control(value=None):
  return dmc.Stack(
    id='annotations-input',
    children=[
      dcc.Store(id='annotations-store', storage_type='local', data=value or []),
      dmc.Text('Annotations', size='md'),
      dmc.Divider(),
      dmc.Stack(id='annotations-container', children=[], gap='sm'),
      add_annotation_button,
      edit_annotation_modal(),
      remove_annotation_modal(),
    ],
  )


__all__ = [
  'annotations_control',
  'add_annotation_button',
  'edit_annotation_modal',
  'handle_edit_modal',
  'handle_remove_annotation_modal',
  'populate_annotation_form',
  'remove_annotation_modal',
  'render_annotations',
  'sync_annotations',
]
