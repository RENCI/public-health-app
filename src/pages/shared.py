from dash import dcc, html, Input, Output, State, callback, exceptions, register_page
import dash_mantine_components as dmc
from src.components.chart import chart
from src.util.insight import extract_controls_from_share_url
from dash_iconify import DashIconify
from src.components.viz_editor import visualization_editor
from src.components.tooltip import tooltip

# this path gets used in util.insight.extract_controls_from_share_url,
# so ensure that `encoded` there stays aligned with path_template here.
register_page(__name__, path_template='/shared/<compressed>', name='Shared Insight')

banner = dmc.Alert(
  'You are viewing a custom insight shared by another user. This content has not been reviewed or validated by the Modeling Hub. Interpret the results carefully—these insights may be exploratory or experimental.',
  color='yellow',
  title='Shared Insight',
  withCloseButton=False,
  my='md',
)

loading_shared_insight = [
  dmc.Flex(  # toolbar
    children=[
      dmc.Skeleton(h=36, w=75),
      dmc.Group([dmc.Skeleton(h=36, w=36), dmc.Skeleton(h=36, w=36), dmc.Skeleton(h=36, w=107)]),
    ],
    justify='space-between',
    align='center',
    mb=24,
  ),
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

layout = dmc.Container(
  id='shared-insight-view-container',
  children=loading_shared_insight,
  size=1200,
)


@callback(
  Output('shared-insight-view-container', 'children'),
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

  explorer_button = tooltip(
    label='Open in Insight Explorer',
    children=dcc.Link(
      dmc.Button(
        'Explore',
        leftSection=DashIconify(icon='feather:arrow-up-right'),
      ),
      id='explorer-button',
      href=f'/explorer?starter=???',
    ),
  )

  return [
    dmc.Flex(  # toolbar
      children=[back_button, dmc.Group([save_button, download_button, explorer_button])],
      justify='space-between',
      align='center',
      mb=24,
    ),
    banner,
    dmc.Title(title, order=1),
    dmc.Divider(my=24),
    html.Div(
      visualization_editor(control_values=controls, show_controls=False),
      style=dict(margin='24px 0'),
    ),
    dcc.Markdown(description),
  ]
