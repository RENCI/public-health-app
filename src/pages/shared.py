from dash import dcc, html, Input, Output, State, callback, exceptions, register_page
import dash_mantine_components as dmc
from src.components.chart import chart
from src.util.insight import extract_controls_from_share_url


# this path gets used in util.insight.extract_controls_from_share_url,
# so ensure that `encoded` there stays aligned with path_template here.
register_page(__name__, path_template='/shared/<compressed>', name='Shared Insight')


back_button = dmc.Anchor('← Home', href='/', id='back-button')

insight_toolbar = dmc.Flex(
  children=[back_button],
  justify='space-between',
  align='center',
  mb=24,
)

banner = dmc.Alert(
  'You are viewing a custom insight shared by another user. This content has not been reviewed or validated by the Modeling Hub. Interpret the results carefully—these insights may be exploratory or experimental.',
  color='yellow',
  title='Shared Insight',
  withCloseButton=False,
  my='md',
)

layout = dmc.Container(
  [
    insight_toolbar,
    banner,
    dmc.Title(id='shared-insight-view-title', order=1, children=''),
    dmc.Divider(my=24),
    html.Div(id='shared-insight-view-figure-container', style=dict(margin='24px 0'), children=''),
    dcc.Markdown(id='shared-insight-view-description'),
  ],
  size=1200,
)


@callback(
  Output('shared-insight-view-title', 'children'),
  Output('shared-insight-view-figure-container', 'children'),
  Output('shared-insight-view-description', 'children'),
  Input('url', 'pathname'),
  Input('url', 'search'),
  State('selected-round-store', 'data'),
  State('custom-insights-store', 'data'),
)
def render_shared_insight(pathname, search, selected_round, custom_insights):
  state = extract_controls_from_share_url(pathname)

  if not state:
    raise exceptions.PreventUpdate

  controls = state.get('controls', {})
  title = state.get('title')
  description = state.get('description')

  return title, chart(control_values=controls), description
