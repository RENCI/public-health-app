import dash_mantine_components as dmc
from dash import dcc
from .ui import (
  annotation_type_select,
  annotation_value_input,
  annotation_label_input,
  annotation_color_input,
)


def edit_annotation_modal():
  return dmc.Modal(
    id='annotation-modal',
    title='Annotation Details',
    children=[
      dmc.Divider(mb=12),
      dmc.Stack(
        [
          annotation_type_select(),
          annotation_value_input(),
          annotation_label_input(),
          annotation_color_input(),
        ],
        gap='md',
        id='annotation-form-container',
      ),
      dmc.Group(
        [
          dmc.Button('Cancel', id='cancel-edit-annotation-button', variant='outline'),
          dmc.Button('Confirm', id='confirm-edit-annotation-button', variant='filled'),
        ],
        justify='flex-end',
        mt='md',
      ),
      dcc.Store(id='edit-index-store', data=None),
    ],
    opened=False,
    centered=True,
  )


def remove_annotation_modal():
  return dmc.Modal(
    id='remove-annotation-modal',
    title='Confirm Deletion',
    children=[
      dmc.Divider(mb=12),
      dmc.Text('Are you sure you want to delete this annotation?'),
      dmc.Group(
        [
          dmc.Button('Keep it', id='cancel-remove-annotation-button', variant='outline'),
          dmc.Button('Delete it', id='confirm-remove-annotation-button', color='crimson'),
        ],
        justify='flex-end',
        mt='md',
      ),
    ],
    opened=False,
    centered=True,
  )
