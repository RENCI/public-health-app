from dash import callback, dcc, exceptions, Input, Output, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify


def zoom_control(value={}):
  x_min = value.get('x', {}).get('min')
  x_max = value.get('x', {}).get('max')
  y_min = value.get('y', {}).get('min')
  y_max = value.get('y', {}).get('max')

  return dmc.Stack(
    children=[
      dcc.Store(id='zoom-control', data=value),
      dmc.Flex(
        [
          dmc.Text('Zoom', size='md'),
          dmc.Button(
            'Fit to Data',
            leftSection=DashIconify(icon='feather:maximize'),
            id='zoom-fit-button',
            variant='subtle',
            size='sm',
          ),
        ],
        justify='space-between',
      ),
      dmc.Divider(),
      dmc.Flex(
        [
          dmc.DateInput(id='zoom-x-min', label='X min', value=x_min),
          dmc.DateInput(id='zoom-x-max', label='X max', value=x_max),
          dmc.NumberInput(id='zoom-y-min', label='Y min', value=y_min, step=100),
          dmc.NumberInput(id='zoom-y-max', label='Y max', value=y_max, step=100),
        ],
        gap='sm',
      ),
    ]
  )


@callback(
  Output('zoom-control', 'data'),
  Input('zoom-x-min', 'value'),
  Input('zoom-x-max', 'value'),
  Input('zoom-y-min', 'value'),
  Input('zoom-y-max', 'value'),
  Input('chart-figure', 'relayoutData'),
  Input('zoom-fit-button', 'n_clicks'),
  State('zoom-control', 'data'),
  prevent_initial_call=True,
)
def update_zoom(x_min, x_max, y_min, y_max, relayout, fit_clicks, current_zoom):
  zoom = current_zoom or {'x': {'min': None, 'max': None}, 'y': {'min': None, 'max': None}}

  # updates from inputs
  zoom['x']['min'] = x_min
  zoom['x']['max'] = x_max
  zoom['y']['min'] = y_min
  zoom['y']['max'] = y_max

  # update from graph drag/zoom
  if relayout and 'xaxis.range[0]' in relayout:
    zoom['x']['min'] = relayout['xaxis.range[0]']
    zoom['x']['max'] = relayout['xaxis.range[1]']
  if relayout and 'yaxis.range[0]' in relayout:
    zoom['y']['min'] = relayout['yaxis.range[0]']
    zoom['y']['max'] = relayout['yaxis.range[1]']

  return zoom


@callback(
  Output('zoom-control', 'data', allow_duplicate=True),
  Output('zoom-x-min', 'value'),
  Output('zoom-x-max', 'value'),
  Output('zoom-y-min', 'value'),
  Output('zoom-y-max', 'value'),
  Input('zoom-fit-button', 'n_clicks'),
  prevent_initial_call=True,
)
def fit_to_data(n_clicks):
  if not n_clicks:
    raise exceptions.PreventUpdate

  # reset store to None (autoranges) but should reset to yaml, if there
  zoom = {
    'x': {'min': None, 'max': None},
    'y': {'min': None, 'max': None},
  }

  # reset UI inputs to blank
  return zoom, None, None, None, None
