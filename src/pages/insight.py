from datetime import datetime
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
from src.components.viz_editor import visualization_editor
from src.data.rounds.round19 import get_insight
from src.util.export.pdf import generate_insight_pdf
from src.util.slugify import slugify

register_page(__name__, path_template='/insight/<insight_id>', name='Insight Details')

loading_insight = [
  dmc.Title(id='insight-view-title', order=1, children=dmc.Skeleton(h=85)),
  dmc.Divider(my=24),
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

back_button = dmc.Anchor(
  '← Back to Round Overview',
  id='back-to-insights-button',
  href='/',
)

explorer_button = dcc.Link(
  dmc.Button(
    'Explore',
    leftSection=DashIconify(icon='feather:arrow-up-right'),
  ),
  id='explorer-button',
  href='#',
)

download_button = dmc.ActionIcon(
  DashIconify(icon='feather:download'),
  variant='subtle',
  id='download-insight-button',
  size='lg',
  loading=False,
)

insight_toolbar = dmc.Flex(
  children=[
    back_button,
    dmc.Group(
      [
        tooltip(download_button, label='Download PDF'),
        tooltip(explorer_button, label="Explore this insight's data"),
      ]
    ),
  ],
  justify='space-between',
  align='center',
  mb=24,
)

def annotations_list(annotations: list):
  if len(annotations) == 0:
    return dmc.Box('')

  annotations_list = [
    dmc.Title('Annotations', order=2),
  ]

  date_annotations = [dmc.ListItem(
    dmc.Text([
      dmc.Text(f'{annotation["label"]}: ', fw=700, span=True),
      f'{datetime.fromisoformat(annotation["value"]).strftime("%B %-d, %Y")}',
    ]), c=annotation['color'])
    for annotation in annotations if annotation['type'] == 'vertical'
  ]

  value_annotations = [dmc.ListItem(
    dmc.Text([
      dmc.Text(f'{annotation["label"]}: ', fw=700, span=True),
      f'{annotation["value"]:,}',
    ]), c=annotation['color'])
    for annotation in annotations if annotation['type'] == 'horizontal'
  ]

  if len(value_annotations) > 0:
    annotations_list.extend([
      dmc.Title('Notable Values', order=3),
      dmc.List(value_annotations),
    ])

  if len(date_annotations) > 0:
    annotations_list.extend([
      dmc.Title('Notable Dates', order=3),
      dmc.List(date_annotations)
    ])
  
  return dmc.Stack(annotations_list)


layout = dmc.Container(
  children=[
    insight_toolbar,
    dmc.Box(
      loading_insight,
      id='insight-view-container',
    ),
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
    annotations = controls['annotations'] or []

    return [
      dmc.Title(insight.get('title', 'Untitled Insight'), order=1),
      dmc.Divider(my=24),
      html.Div(
        visualization_editor(control_values=controls, show_controls=False),
        style=dict(margin='24px 0'),
      ),
      annotations_list(annotations),
      dmc.Title('Description', order=2, my=12),
      dcc.Markdown(insight.get('description', '')),
      dcc.Download(id='insight-pdf-download'),
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
