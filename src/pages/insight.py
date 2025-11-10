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

from src.components.tooltip import tooltip
from src.components.toolbar import toolbar, toolbar_button
from src.components.viz_editor import visualization_editor
from src.components.insight_yaml_modal import insight_yaml_modal_button, insight_yaml_modal
from src.data.rounds.round19 import get_insight
from src.util.data import load_rounds
from src.util.export.pdf import generate_insight_pdf
from src.util.slugify import slugify

register_page(__name__, path_template='/insight/<insight_id>', name='Insight Details')

back_button = dmc.Anchor(
  toolbar_button('Round Summary', icon=DashIconify(icon='feather:chevron-left')),
  id='back-to-insights-button',
  href='/',
)


download_button = toolbar_button(
  'PDF',
  icon=DashIconify(icon='feather:download'),
  id='download-insight-button',
  loading=False,
)


explorer_button = dmc.Anchor(
  toolbar_button(
    'Explore',
    icon=DashIconify(icon='feather:arrow-up-right'),
    variant='gradient',
    gradient={'from': 'lime', 'to': 'teal', 'deg': 120},
  ),
  id='explorer-button',
  href='#',
)


insight_toolbar = toolbar(
  left=[back_button], right=[insight_yaml_modal_button(), download_button, explorer_button]
)


loading_insight = [
  dmc.Space(h=16),
  dmc.Title(id='insight-view-title', order=1, children=dmc.Skeleton(h=82)),
  insight_toolbar,
  html.Div(
    id='insight-view-figure-container',
    children=dmc.Stack(
      [
        dmc.Skeleton(h=600),
        dmc.Space(h=24),
        dmc.Stack([dmc.Skeleton(h=30), dmc.Skeleton(h=30), dmc.Skeleton(h=30)]),
      ]
    ),
    style=dict(margin='24px 0'),
  ),
  dcc.Markdown(id='insight-view-description'),
  dcc.Download(id='insight-pdf-download'),
]


def insight_heading(round_number: str, round_date: str, round_name: str):
  return dmc.Stack(
    [
      dmc.Text(
        f'Round {round_number}',
        style=dict(fontSize='var(--mantine-h3-font-size'),
        c='dimmed',
        fw=700,
        mb=8,
      ),
      dmc.Flex(
        [
          dmc.Text(round_name, style=dict(fontSize='var(--mantine-h2-font-size'), fw=700),
          dmc.Text(f'Date completed: {round_date}', c='dimmed', style=dict(fontStyle='italic')),
        ],
        justify='space-between',
        align='flex-end',
      ),
    ],
    gap=0,
  )


layout = dmc.Container(
  children=[
    dmc.Box(
      loading_insight,
      id='insight-view-container',
    ),
    insight_yaml_modal(),  # getting this in the DOM. will be updated by callback
  ],
  size=1200,
)


@callback(
  Output('explorer-button', 'href'),
  Input('url', 'pathname'),
)
def add_back_link_href(pathname):
  insight_id = pathname.split('/insight/')[-1]
  if not insight_id:
    raise ValueError('No insight ID provided')

  return f'/explorer?starter={insight_id}'


@callback(
  Output('insight-view-container', 'children'),
  Input('url', 'pathname'),
  Input('custom-insights-store', 'data'),
)
def show_insight_details(pathname, custom_insights):
  """Render the insight details page given /insight/<insight_id>"""
  if not pathname or not pathname.startswith('/insight/'):
    raise exceptions.PreventUpdate

  try:
    insight_id = pathname.split('/insight/')[-1]
    if not insight_id:
      raise ValueError('No insight ID provided')

    insight = get_insight(insight_id, custom_insights=custom_insights or [])
    if not insight:
      raise ValueError(f'Insight {insight_id} not found')

    controls = insight.get('controls', {})
    round_number = str(controls['round_num'])

    rounds = load_rounds()
    this_round = rounds.get(round_number)
    if not this_round:
      raise exceptions.PreventUpdate

    return [
      dmc.Space(h=16),
      insight_heading(
        round_number=round_number,
        round_date=this_round.get('date'),
        round_name=this_round.get('name'),
      ),
      insight_toolbar,
      dmc.Title(f'Insight: {insight.get("title", "Untitled Insight")}', order=1),
      dmc.Text(insight.get('summary', 'Summary not found')),
      html.Div(
        visualization_editor(control_values=controls, show_controls=False),
        style=dict(margin='24px 0'),
      ),
      dcc.Markdown(insight.get('description', '')),
      dmc.Space(h=24),
      dcc.Download(id='insight-pdf-download'),
      insight_yaml_modal(insight),
    ]

  except Exception as e:
    return dmc.Alert(
      dmc.Text(f'Error loading insight: "{e}"'),
      color='crimson',
      title='Insight Error',
      p='10rem',
    )


clientside_callback(
  """
  function(n_clicks) {
    if (!n_clicks) return false;  // initial render
    return true;                  // show loading immediately on click
  }
  """,
  Output('download-insight-button', 'loading', allow_duplicate=True),
  Input('download-insight-button', 'n_clicks'),
  prevent_initial_call=True,
)

@callback(
  Output('insight-pdf-download', 'data'),
  Output('notification-container', 'sendNotifications', allow_duplicate=True),
  Output('download-insight-button', 'loading'),
  Input('download-insight-button', 'n_clicks'),
  State('custom-insights-store', 'data'),
  State('url', 'pathname'),
  prevent_initial_call=True,
)
def handle_click_download(n_clicks, custom_insights, pathname):
  if not n_clicks:
    return no_update, no_update, False

  if not pathname or not pathname.startswith('/insight/'):
    raise exceptions.PreventUpdate

  try:
    insight_id = pathname.split('/insight/')[-1]
    if not insight_id:
      raise ValueError('No insight ID provided')

    insight = get_insight(insight_id, custom_insights=custom_insights or [])
    if not insight:
      raise ValueError(f'Insight {insight_id} not found')

    round_number = insight.get('controls', {}).get('round_number', '18')
    slugified_title = slugify(insight.get('title', ''))

    pdf = generate_insight_pdf(insight)
    filename = f'SMH_{round_number}_{slugified_title}.pdf'

    return dcc.send_bytes(pdf, filename), no_update, False

  except Exception as error:
    print(f'Download failed: {error}')
    notification = {
      'action': 'show',
      'id': f'insight-pdf-download-failed-{uuid.uuid4()}',
      'message': 'Download failed!',
      'color': 'crimson',
    }
    return no_update, [notification], False
