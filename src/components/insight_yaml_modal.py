import os

import yaml
import uuid

import dash_mantine_components as dmc
from dash import (
  Input,
  Output,
  State,
  callback,
  clientside_callback,
  dcc,
  exceptions,
  html,
  no_update,
  register_page,
)
from dash_iconify import DashIconify
from src.components.toolbar import toolbar_button

# to use:
#   import insight_yaml_modal and insight_yaml_modal_button.
#   ensure both are in the layout.
#   pass insight dict into insight_yaml_modal.

def insight_yaml_modal(insight = {}):  
  return dmc.Modal(
    [
      dmc.Code(
        yaml.dump(insight),
        id='insight-yaml',
        style=dict(overflow='auto'),
        block=True,
      ),
      dcc.Clipboard(
        target_id='insight-yaml',
        title='copy',
        style=dict(position='absolute', top=72, right=32, fontSize=16),
      ),
    ],
    title='Insight YAML',
    id='insight-yaml-modal',
    opened=False,
    size='lg',
  )


def insight_yaml_modal_button():
  # DASH_ENV=production is set in the Dockerfile,
  # but this can be tested by starting the app with
  # `export DASH_ENV=production && uv run python app.py`.
  if os.environ.get('DASH_ENV') != 'production':
    return toolbar_button(
      'YAML',
      icon=DashIconify(icon='feather:list'),
      id='insight-yaml-modal-button',
    )
  return ''

@callback(
  Output('insight-yaml-modal', 'opened'),
  Input('insight-yaml-modal-button', 'n_clicks'),
  prevent_initial_call=True,
)
def show_modal(n_clicks):
  return True
