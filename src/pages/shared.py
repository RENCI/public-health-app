import datetime
import json
import uuid

import dash_mantine_components as dmc
from dash import Input, Output, State, callback, dcc, exceptions, html, register_page
from dash_iconify import DashIconify
from lzstring import LZString

from src.components.tooltip import tooltip
from src.components.viz_editor import visualization_editor
from src.util import extract_controls_from_share_url

# this path gets used in util.insight.extract_controls_from_share_url,
# so ensure that `encoded` there stays aligned with path_template here.
register_page(__name__, path_template='/shared/<compressed>', name='Shared Insight')

lz = LZString()

banner = dmc.Alert(
  'You are viewing a custom insight shared by another user. This content has not been reviewed or validated by the Modeling Hub. Interpret the results carefully—these insights may be exploratory or experimental.',
  color='yellow',
  title='Shared Insight',
  withCloseButton=False,
  my='md',
)

loading_shared_insight = [
  banner,
  dmc.Skeleton(h=85),
  dmc.Divider(my=24),
  html.Div(
    children=dmc.Stack(
      [
        dmc.Skeleton(h=600),
        dmc.Space(h=24),
        dmc.Stack(
          [
            dmc.Skeleton(h=30),
            dmc.Skeleton(h=30),
            dmc.Skeleton(h=30),
          ]
        ),
      ]
    ),
    style=dict(margin='24px 0'),
  ),
]

back_button = dmc.Anchor('← Home', href='/', id='back-button')

save_button = tooltip(
  label='Save to My Insights',
  children=dmc.ActionIcon(
    DashIconify(icon='feather:save'),
    variant='subtle',
    size='lg',
    id='save-shared-insight-button',
  ),
)

download_button = tooltip(
  label='Download Insight (PDF)',
  children=dmc.ActionIcon(
    DashIconify(icon='feather:download'),
    variant='subtle',
    size='lg',
    id='download-shared-insight-button',
  ),
)

shared_insight_toolbar = dmc.Flex(
  children=[back_button, dmc.Group([save_button, download_button])],
  justify='space-between',
  align='center',
  mb=24,
)

layout = dmc.Container(
  children=[
    shared_insight_toolbar,
    dmc.Box(
      loading_shared_insight,
      id='shared-insight-container',
    ),
  ],
  size=1200,
)


@callback(
  Output('shared-insight-container', 'children'),
  Input('url', 'pathname'),
  State('selected-round-store', 'data'),
  State('custom-insights-store', 'data'),
)
def render_shared_insight(pathname, selected_round, custom_insights):
  state = extract_controls_from_share_url(pathname)

  if not state:
    raise exceptions.PreventUpdate

  controls = state.get('controls', {})
  title = state.get('title')
  description = state.get('description')

  return [
    banner,
    dmc.Title(title, order=1),
    dmc.Divider(my=24),
    html.Div(
      visualization_editor(controls=controls, show_controls=False),
      style=dict(margin='24px 0'),
    ),
    dcc.Markdown(description),
  ]


@callback(
  Output('custom-insights-store', 'data'),
  Output('notification-container', 'sendNotifications'),
  Output('_pages_location', 'pathname', allow_duplicate=True),  # update path
  Input('save-shared-insight-button', 'n_clicks'),
  State('url', 'pathname'),
  State('selected-round-store', 'data'),
  State('custom-insights-store', 'data'),
  prevent_initial_call=True,
)
def save_shared_insight(save_clicks, pathname, selected_round, shared_insights):
  if not save_clicks:
    raise exceptions.PreventUpdate

  if not pathname or not pathname.startswith('/shared/'):
    return None

  now = datetime.datetime.utcnow().isoformat()
  new_id = str(uuid.uuid4())
  compressed = pathname.removeprefix('/shared/')
  new_insight = json.loads(lz.decompressFromEncodedURIComponent(compressed))
  new_insight['id'] = new_id
  new_insight['image_url'] = 'https://placehold.co/400?text=Visualization'
  new_insight['created_at'] = now
  new_insight['updated_at'] = new_insight['created_at']

  notification = {
    'action': 'show',
    'id': f'save-success-{uuid.uuid4()}',
    'message': 'Saved to custom insights successfully!',
    'color': 'limegreen',
  }

  return shared_insights + [new_insight], [notification], f'/insight/{new_id}'
