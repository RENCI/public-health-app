from dash import callback, ctx, dcc, Input, Output, State
import dash_mantine_components as dmc


def zoom_control(value={}):
  x_min = value.get('x', {}).get('min')
  x_max = value.get('x', {}).get('max')
  y_min = value.get('y', {}).get('min')
  y_max = value.get('y', {}).get('max')

  return dmc.Stack(
    children=[
      dcc.Store(id='zoom-store', data=value),
      dmc.Flex(
        [
          dmc.Text('Zoom', size='md'),
          dmc.Button('Use chart zoom', id='use-chart-zoom-button', size='xs', variant='subtle'),
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
  Output('zoom-store', 'data'),
  Input('zoom-x-min', 'value'),
  Input('zoom-x-max', 'value'),
  Input('zoom-y-min', 'value'),
  Input('zoom-y-max', 'value'),
  State('zoom-store', 'data'),
  prevent_initial_call=True,
)
def update_zoom(x_min, x_max, y_min, y_max, current_zoom):
  zoom = current_zoom or {'x': {}, 'y': {}}
  trigger = ctx.triggered_id

  if trigger in ['zoom-x-min', 'zoom-x-max', 'zoom-y-min', 'zoom-y-max']:
    zoom.setdefault('x', {})
    zoom.setdefault('y', {})
    if x_min is not None:
      zoom['x']['min'] = x_min
    if x_max is not None:
      zoom['x']['max'] = x_max
    if y_min is not None:
      zoom['y']['min'] = y_min
    if y_max is not None:
      zoom['y']['max'] = y_max

  return zoom
