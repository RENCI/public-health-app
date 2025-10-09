import uuid

import dash_mantine_components as dmc
from dash import ALL, callback, clientside_callback, ctx, dcc, exceptions, no_update, Input, Output, State
from dash_iconify import DashIconify

from src.util.time_ago import time_ago
from src.util.data import load_rounds
from src.util.export.pdf import generate_round_pdf
from src.util.format_timestamp import format_timestamp
from src.util.slugify import slugify

from src.components.tooltip import tooltip

def tipped_text(text, tooltip=None, size='md'):
  return dmc.Tooltip(
    label=tooltip if tooltip else text,
    position='top',
    withArrow=True,
    children=dmc.Text(text, size=size, c='gray'),
  )


no_insights_message = dmc.Card(
  dmc.Center(
    dmc.Stack(
      [
        dmc.Text("You haven't added any insights for this round yet."),
        dmc.Text('Start exploring the data and build your first custom insight!'),
        dmc.Anchor(
          dmc.Button(
            [
              'Build a custom insight',
              dmc.Space(w=8),
              DashIconify(icon='feather:arrow-right', width=20),
            ],
            variant='gradient',
            gradient={'from': 'lime', 'to': 'teal', 'deg': 120},
            style=dict(
              textDecoration='none',
              display='flex',
              justifyContent='center',
              alignItems='center',
              minHeight='100%',
            ),
          ),
          href='/explorer',
          size='lg',
          underline=False,
        ),
      ],
      ta='center',
      gap=8,
      align='center',
    ),
    h=150,
  ),
  p=0,
)

new_insight_prompt = dmc.Card(
  dmc.Center(
    [
      dmc.Anchor(
        dmc.Button(
          [
            'Build a new custom insight',
            dmc.Space(w=8),
            DashIconify(icon='feather:arrow-right', width=20),
          ],
          variant='gradient',
          gradient={'from': 'lime', 'to': 'teal', 'deg': 120},
          style=dict(
            textDecoration='none',
            display='flex',
            justifyContent='center',
            alignItems='center',
            minHeight='100%',
          ),
        ),
        href='/explorer',
        size='lg',
        underline=False,
      ),
    ],
    h=150,
  ),
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
    href=f'/insight?id={item["id"]}',
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
    withBorder=True,
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
    href=f'/insight?id={item["id"]}',
    underline=False,
  )

  delete_button = dmc.Button(
    [DashIconify(icon='feather:trash-2', width=20)],
    id={'type': 'delete-insight', 'id': item['id']},
    variant='light',
    color='red',
    style=dict(
      textDecoration='none',
      display='flex',
      justifyContent='center',
      alignItems='center',
    ),
  )

  custom_insights_badge = dmc.Badge(
    'Custom',
    variant='gradient',
    gradient={'from': 'lime', 'to': 'teal', 'deg': 120},
    size='md',
    radius='md',
  )

  return dmc.Card(
    [
      graphic,
      dmc.Stack(
        [
          title,
          dmc.Flex(
            [
              dmc.Group(
                [
                  custom_insights_badge,
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
        justify='space-between',
        style=dict(flex=1),
        gap=8,
      ),
    ],
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

download_button = dmc.ActionIcon(
  DashIconify(icon='feather:download'),
  id='download-round-button',
  variant='subtle',
  size='lg',
  loading=False,
)


def round_summary():
  return dmc.Stack(
    [
      delete_modal,
      dmc.Space(h=24),
      dmc.Flex(
        [
          dmc.Title(id='round-title', order=1),
          tooltip(download_button, label='Download PDF'),
        ],
        justify='space-between',
        align='flex-end',
      ),
      dmc.Divider(),
      dmc.Box(id='round-overview'),
      dmc.Title('Insights', order=2, my=16),
      dmc.Stack(id='insights-list', gap='md'),
      dmc.Stack(id='custom-insights-list', gap='md'),
      dcc.Download(id='round-pdf-download'),
    ],
    gap='md',
  )


@callback(
  Output('round-title', 'children'),
  Output('round-overview', 'children'),
  Output('insights-list', 'children'),
  Input('selected-round-store', 'data'),
  Input('url', 'pathname'),
)
def update_round_summary(round_number, pathname):
  if not round_number:
    return 'No round selected', '...', []
  rounds = load_rounds()
  this_round = rounds.get(round_number)
  if not this_round:
    return f'Round {round_number}', 'No data.', []

  report = this_round.get('report') or '...'
  insights = this_round.get('insights') or []
  return f'Round {round_number}', dcc.Markdown(report), [insight_button(i) for i in insights]


@callback(
  Output('custom-insights-list', 'children'),
  Input('custom-insights-store', 'data'),
  Input('selected-round-store', 'data'),
)
def update_custom_insights_list(custom_insights, round_number):
  if not custom_insights or not round_number:
    return [no_insights_message]

  filtered = [
    insight
    for insight in custom_insights
    if str(insight.get('controls', {}).get('round')) == str(round_number)
  ]
  return [custom_insight_button(i) for i in filtered] + [new_insight_prompt] or [
    no_insights_message
  ]


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


clientside_callback(
  """
  function(n_clicks) {
    if (!n_clicks) return false;  // initial render
    return true;                  // show loading immediately on click
  }
  """,
  Output('download-round-button', 'loading', allow_duplicate=True),
  Input('download-round-button', 'n_clicks'),
  prevent_initial_call=True,
)


@callback(
  Output('round-pdf-download', 'data'),
  Output('notification-container', 'sendNotifications', allow_duplicate=True),
  Output('download-round-button', 'loading'),
  Input('download-round-button', 'n_clicks'),
  State('selected-round-store', 'data'),
  State('url', 'search'),
  prevent_initial_call=True,
)
def handle_click_download(n_clicks, round_number, search):
  if not n_clicks:
    return no_update, no_update, False

  try:
    if not round_number:
      raise exceptions.PreventUpdate

    rounds = load_rounds()
    this_round = rounds.get(round_number)

    if not this_round:
      raise exceptions.PreventUpdate

    slugified_name = slugify(this_round.get('name', ''))

    pdf = generate_round_pdf(this_round)
    filename = f'SMH-round-{round_number}_{slugified_name}.pdf'

    return dcc.send_bytes(pdf, filename), no_update, False

  except Exception as error:
    print(f'Download failed: {error}')
    notification = {
      'action': 'show',
      'id': f'round-pdf-download-failed-{uuid.uuid4()}',
      'message': 'Download failed!',
      'color': 'crimson',
    }
    return no_update, [notification], False
