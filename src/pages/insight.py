import dash_mantine_components as dmc
from dash import exceptions, html, Input, Output, callback, dcc, register_page
from dash_iconify import DashIconify
from src.data.rounds.round19 import get_insight
from src.components.viz_editor import visualization_editor

register_page(__name__, path_template='/insight/<insight_id>', name='Insight Details')

loading_insight = [
  dmc.Flex(  # toolbar
    children=[
      dmc.Skeleton(h=36, w=200),
      dmc.Group([dmc.Skeleton(h=36, w=36), dmc.Skeleton(h=36, w=110)]),
    ],
    justify='space-between',
    align='center',
    mb=24,
  ),
  dmc.Title(id='insight-view-title', order=1, children=dmc.Skeleton(h=85)),
  dmc.Divider(my=24),
  html.Div(
    id='insight-view-figure-container',
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
  dcc.Markdown(id='insight-view-description'),
]

layout = dmc.Container(
  id='insight-view-container',
  children=loading_insight,
  size=1200,
)


@callback(
  Output('insight-view-container', 'children'),
  Input('url', 'pathname'),
  Input('custom-insights-store', 'data'),
)
def show_insight_details(pathname, custom_insights):
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
      href=f'/explorer?starter={insight_id}',
    )

    download_button = dcc.Link(
      dmc.ActionIcon(DashIconify(icon='feather:download'), variant='subtle', size='lg'),
      id='download-button',
      href='#',
    )

    return [
      dmc.Flex(  # toolbar
        children=[back_button, dmc.Group([download_button, explorer_button])],
        justify='space-between',
        align='center',
        mb=24,
      ),
      dmc.Title(insight.get('title', 'Untitled Insight'), order=1),
      dmc.Divider(my=24),
      html.Div(
        visualization_editor(control_values=controls, show_controls=False),
        style=dict(margin='24px 0'),
      ),
      dcc.Markdown(insight.get('description', '')),
    ]

  except Exception as e:
    return dmc.Alert(
      dmc.Text(f'Error loading insight: "{e}"'),
      color='crimson',
      title='Insight Error',
      p='10rem',
    )
