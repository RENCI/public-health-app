from urllib.parse import parse_qs

import dash_mantine_components as dmc
from dash import html, Input, Output, callback, dcc, no_update, register_page
from dash_iconify import DashIconify
from src.data.rounds.round19 import get_insight
from src.util.get_query_param import get_query_param
from src.components.viz_editor import visualization_editor

register_page(__name__, path_template='/insight', name='Insight Details')

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
download_button = dcc.Link(
  dmc.Button(
    'Download',
    leftSection=DashIconify(icon='feather:download'),
    variant='outline',
  ),
  id='download-button',
  href='#',
)

toolbar = dmc.Flex(
  children=[back_button, dmc.Group([download_button, explorer_button])],
  justify='space-between',
  align='center',
  mb=24,
)

loading_title = dmc.Skeleton(h=85)
loading_chart = dmc.Skeleton(h=600)
loading_description = dmc.Stack(
  [
    dmc.Skeleton(h=30),
    dmc.Skeleton(h=30),
    dmc.Skeleton(h=30),
  ]
)
loading_details = dmc.Stack(
  [
    loading_chart,
    dmc.Space(h=24),
    loading_description,
  ]
)

layout = dmc.Container(
  [
    toolbar,
    dmc.Title(id='insight-view-title', order=1, children=loading_title),
    dmc.Divider(my=24),
    html.Div(
      id='insight-view-figure-container', style=dict(margin='24px 0'), children=loading_details
    ),
    dcc.Markdown(id='insight-view-description'),
  ],
  size=1200,
)


@callback(
  Output('insight-view-figure-container', 'children'),
  Output('insight-view-title', 'children'),
  Output('insight-view-description', 'children'),
  Input('url', 'pathname'),
  Input('url', 'search'),
  Input('custom-insights-store', 'data'),
)
def show_details(pathname, search, custom_insights):
  if pathname != '/insight':
    # prevent rendering insight view if we're heading to another page
    return no_update, no_update, no_update

  try:
    insight_id = get_query_param(search, 'id')
    if not insight_id:
      raise ValueError('No insight ID in URL')

    insight = get_insight(insight_id, custom_insights=custom_insights or [])
    if not insight:
      raise ValueError(f'Insight {insight_id} not found')

    controls = insight.get('controls', {})

    return (
      visualization_editor(control_values=controls, show_controls=False),
      insight.get('title', 'Untitled Insight'),
      insight.get('description', ''),
    )

  # fallback
  except Exception as e:
    return (
      dmc.Alert(f'Error loading insight: {e}', color='crimson', title='Insight Error'),
      'Error',
      '',
    )


@callback(
  Output('explorer-button', 'href'),
  Input('url', 'search'),
)
def add_back_link_href(search):
  query = parse_qs(search.lstrip('?'))
  insight_id = query.get('id', [None])[0]
  return f'/explorer?starter={insight_id}'
