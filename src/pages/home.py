import uuid

import dash_mantine_components as dmc
from dash import (
  ALL,
  Input,
  Output,
  State,
  callback,
  ctx,
  dcc,
  exceptions,
  no_update,
  register_page,
)
from dash_iconify import DashIconify

from src.components.insight_report import insight_report

from src.util.format_timestamp import format_timestamp
from src.util.time_ago import time_ago

from ..data.round19 import insights

register_page(__name__, path='/')


def tipped_text(text, tooltip=None, size='md'):
  return dmc.Tooltip(
    label=tooltip if tooltip else text,
    position='top',
    withArrow=True,
    children=dmc.Text(text, size=size, c='gray'),
  )


def insight_button(item):
  graphic = dmc.Image(
    src=item['image_url'], radius='sm', style=dict(width='125px', height='125px', objectFit='cover')
  )

  title = dmc.Text(item['title'], size='lg', style=dict(whiteSpace='normal', textAlign='left'))

  description = dcc.Markdown(item['description'], style=dict(fontSize='75%'))

  view_button = dmc.Anchor(
    dmc.Button(
      ['View', dmc.Space(w=8), DashIconify(icon='feather:arrow-right', width=20)],
      variant='light',
      style=dict(
        textDecoration='none',
        display='flex',
        justifyContent='center',
        alignItems='center',
        minHeight='100%',
      ),
    ),
    href=f'/viewer?id={item["id"]}',
    underline=False,
  )

  return dmc.Card(
    [
      graphic,
      dmc.Stack(
        [title, description],
        align='flex-start',
        style=dict(flex=1, overflow='hidden'),
      ),
      view_button,
    ],
    variant='soft',
    style=dict(
      display='flex',
      gap='1rem',
      justifyContent='flex-start',
      alignItems='stretch',
      minHeight='150px',
      maxHeight='150px',
      padding='1rem',
      flexDirection='row',
    ),
  )


def custom_insight_button(item):
  created_at = item.get('created_at', None)
  updated_at = item.get('updated_at', None)

  graphic = dmc.Image(
    src=item['image_url'], radius='sm', style=dict(width='125px', height='125px', objectFit='cover')
  )

  title = dmc.Text(item['title'], size='lg', style=dict(whiteSpace='normal', textAlign='left'))

  description = dcc.Markdown(item['description'], style=dict(fontSize='75%', overflow='hidden'))

  view_button = dmc.Anchor(
    dmc.Button(
      ['View', dmc.Space(w=8), DashIconify(icon='feather:arrow-right', width=20)],
      variant='light',
      style=dict(
        textDecoration='none',
        display='flex',
        justifyContent='center',
        alignItems='center',
      ),
    ),
    href=f'/viewer?id={item["id"]}',
    underline=False,
  )

  delete_button = dmc.Button(
    [DashIconify(icon='feather:trash-2', width=20)],
    id={'type': 'delete-insight', 'id': item['id']},
    variant='light',
    c='red',
    style=dict(
      textDecoration='none',
      display='flex',
      justifyContent='center',
      alignItems='center',
    ),
  )

  return dmc.Card(
    [
      graphic,
      dmc.Stack(
        [
          title,
          description,
          dmc.Flex(
            [
              dmc.Group(
                [
                  tipped_text(
                    f'Created: {format_timestamp(created_at)}', time_ago(created_at), size='xs'
                  ),
                  tipped_text(
                    f'Last updated: {format_timestamp(updated_at)}', time_ago(updated_at), size='xs'
                  ),
                ]
              ),
              dmc.Group(
                [
                  delete_button,
                  view_button,
                ],
                align='flex-end',
              ),
            ],
            justify='space-between',
            align='flex-end',
            style=dict(width='100%'),
          ),
        ],
        align='flex-start',
        style=dict(flex=1),
      ),
    ],
    variant='soft',
    style=dict(
      display='flex',
      gap='1rem',
      justifyContent='flex-start',
      alignItems='stretch',
      minHeight='150px',
      maxHeight='200px',
      padding='1rem',
      flexDirection='row',
    ),
  )

no_insights_message = dmc.Card(
  dmc.Center(
    dmc.Stack(
      [
        dmc.Text("It looks like you haven't created any custom insights yet."),
        dmc.Text(
          ['Head over to the ', dmc.Anchor('Explorer', href='/explorer'), ' to build one!']
        ),
      ],
      ta='center',
      gap=24,
    ),
    h=300,
  ),
  my=16,
)

delete_modal = dmc.Modal(
  id='delete-confirmation-modal',
  title='Confirm Deletion',
  children=[
    dmc.Text('Are you sure you want to delete this insight?'),
    dmc.Group(
      [
        dmc.Button('Cancel', id='cancel-delete', variant='outline'),
        dmc.Button('Delete', id='confirm-delete', color='red'),
      ],
      justify='flex-end',
      mt='md',
    ),
  ],
  opened=False,
  centered=True,
)

disclaimer = dcc.Markdown(f'''
    The US COVID-19 Scenario Modeling Hub aims to produce robust projections to provide real-time actionable modeling
    evidence to support ongoing public health needs and decision-making. For Round 19, eight teams contributed both national
    and state-specific projections of the trajectory of COVID-19 during April 27, 2025 to April 25, 2026. Detailed scenario
    descriptions and setting assumptions are provided on the SMH GitHub site. See covid19scenariomodelinghub.org for more
    results and details.
  ''', style=dict(color='gray'))

layout = dmc.Container(
  [
    dmc.Tabs(
      [
        dmc.Flex([
          dmc.Title(f'Round 19', order=1, my=24, style=dict(textAlign='center')),
          dmc.TabsList(
            [
              dmc.TabsTab('Round Details', value='round-details', p=8, color='gray'),
              dmc.TabsTab('Round Insights', value='round-insights', p=8, color='gray'),
              dmc.TabsTab('Custom Insights', value='custom-insights', p=8, color='gray'),
            ],
            grow=False,
          )],
          justify='space-between',
          align='center',
        ),
        dmc.TabsPanel(
          insight_report,
          value='round-details',
        ),
        dmc.TabsPanel(
          dmc.Stack(
            [insight_button(item) for item in insights],
            id='insights-list',
            gap='md',
            my=24,
            style=dict(width='100%'),
          ),
          value='round-insights',
        ),
        dmc.TabsPanel(
          dmc.Stack(
            [no_insights_message],
            id='custom-insights-list',
            gap='md',
            p=24,
            style=dict(width='100%'),
          ),
          value='custom-insights',
        ),
      ],
      value='round-details',
      variant='pills',
      autoContrast=True,
    ),
    dmc.Divider(my=48),
    disclaimer,
    delete_modal,
  ],
)


@callback(
  Output('custom-insights-list', 'children'),
  Input('custom-insights-store', 'data'),
  prevent_initial_call=False,
)
def update_insights_list(custom_data):
  if not custom_data or len(custom_data) == 0:
    return [no_insights_message]
  return [custom_insight_button(item) for item in custom_data]


@callback(
  Output('delete-confirmation-modal', 'opened', allow_duplicate=True),
  Output('delete-confirmation-modal', 'data', allow_duplicate=True),
  Output('custom-insights-store', 'data', allow_duplicate=True),
  Output('notification-container', 'sendNotifications', allow_duplicate=True),
  Input({'type': 'delete-insight', 'id': ALL}, 'n_clicks'),
  Input('cancel-delete', 'n_clicks'),
  Input('confirm-delete', 'n_clicks'),
  State('delete-confirmation-modal', 'data'),
  State('custom-insights-store', 'data'),
  prevent_initial_call=True,
)
def handle_delete(delete_clicks, cancel_click, confirm_click, modal_data, custom_insights):
  triggered = ctx.triggered_id

  # defaults
  # opened, data, updated_store, notifications = False, no_update, no_update, no_update

  # Case 1: delete button clicked → open modal
  if isinstance(triggered, dict) and triggered.get('type') == 'delete-insight':
    if not any(delete_clicks):
      raise exceptions.PreventUpdate
    return True, triggered['id'], no_update, no_update

  # Case 2: cancel → just close modal
  if triggered == 'cancel-delete':
    return False, no_update, no_update, no_update

  # Case 3: confirm → actually delete
  if triggered == 'confirm-delete' and modal_data:
    insight_id = modal_data
    if not custom_insights:
      raise exceptions.PreventUpdate

    deleted = next((ci for ci in custom_insights if ci['id'] == insight_id), None)
    updated = [ci for ci in custom_insights if ci['id'] != insight_id]

    notification = {
      'action': 'show',
      'id': f'delete-success-{uuid.uuid4()}',
      'message': f'Insight "{deleted["title"].strip()}" deleted successfully!'
      if deleted
      else 'Insight deleted.',
      'color': 'green',
    }

    return False, no_update, updated, [notification]

  raise exceptions.PreventUpdate
