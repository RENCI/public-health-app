import uuid
from datetime import datetime

import dash_mantine_components as dmc
import markdown
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
from src.util import generate_insight_pdf, load_rounds, slugify

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

def annotations_list(annotations: list):
  if len(annotations) == 0:
    return dmc.Box('')

  list_items = []

  date_annotations = [
    dmc.ListItem(
      dmc.Text(
        children=[
          dmc.Text(f'{annotation["label"]}: ', fw=700, span=True),
          f'{datetime.fromisoformat(annotation["value"]).strftime("%B %-d, %Y")}',
        ],
        id=annotation['label'],
        c=annotation['color'],
        className=f'annotation-ref vertical {annotation["label"]}',
        **{'data-annotation-ref': slugify(annotation['label'])},
      ),
      id={'type': 'annotation-item', 'id': annotation['label']},
    )
    for annotation in annotations
    if annotation['type'] == 'vertical'
  ]

  value_annotations = [
    dmc.ListItem(
      dmc.Text(
        children=[
          dmc.Text(f'{annotation["label"]}: ', fw=700, span=True),
          f'{annotation["value"]:,}',
        ],
        id=annotation['label'],
        c=annotation['color'],
        className=f'annotation-ref horizontal {annotation["label"]}',
        **{'data-annotation-ref': slugify(annotation['label'])},
      ),
      id={'type': 'annotation-item', 'id': annotation['label']},
    )
    for annotation in annotations
    if annotation['type'] == 'horizontal'
  ]

  if len(value_annotations) > 0:
    list_items.extend(
      [
        dmc.Title('Notable Values', order=3),
        dmc.List(value_annotations),
      ]
    )

  if len(date_annotations) > 0:
    list_items.extend([dmc.Title('Notable Dates', order=3), dmc.List(date_annotations)])

  return list_items


layout = dmc.Container(
  children=[
    insight_toolbar,
    dmc.Box(id='dummy-output'),
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
  Input('theme-store', 'data'),
)
def show_insight_details(pathname, custom_insights, theme):
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
    controls = {**controls, 'theme': theme}
    annotations = controls.get('annotations', [])
    round_number = str(controls.get('round_num', '18'))
    rounds = load_rounds()
    this_round = rounds.get(round_number)

    return [
      dmc.Space(h=16),
      insight_heading(
        round_number=round_number,
        round_date=this_round.get('date'),
        round_name=this_round.get('name'),
      ),
      dmc.Title(f'Insight: {insight.get("title", "Untitled Insight")}', order=1),
      dmc.Text(insight.get('summary', 'Summary not found')),
      html.Div(
        visualization_editor(controls=controls, show_controls=False),
        style=dict(margin='24px 0'),
      ),
      dmc.Grid([
        dmc.GridCol([
          dmc.Title('Discussion', order=2, my=12),
          dcc.Markdown(
            markdown.markdown(insight.get('description', ''), extensions=['extra']),
            dangerously_allow_html=True,
            style=dict(lineHeight=2),
          ),
        ], span=dict(base=12, md=7 if len(annotations) else 12)),
        dmc.GridCol(
          dmc.Card(
            dmc.Stack(annotations_list(annotations), id='annotations-list-container'),
            variant='soft',
            p='lg',
          ),
          span=dict(base=12, md=5),
        ) if len(annotations) else None,
      ]),
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
  function() {
    if (typeof window.attachAnnotationListeners === 'function') {
      window.attachAnnotationListeners();
    }
    return null;
  }
  """,
  Output('dummy-output', 'children'),
  Input('insight-view-container', 'children'),
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
