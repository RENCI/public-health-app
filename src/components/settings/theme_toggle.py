from dash import ctx, Dash, dcc, Input, Output, State, callback, _dash_renderer
import dash_mantine_components as dmc
from dash_iconify import DashIconify

# persist in local storage
theme_persistence = dcc.Store(
  id='theme-store',
  storage_type='local',
)

theme_toggle = dmc.ActionIcon(
  [
    theme_persistence,
    dmc.Box(DashIconify(icon='feather:moon', width=24, height=24), darkHidden=True),
    dmc.Box(DashIconify(icon='feather:sun', width=24, height=24), lightHidden=True),
  ],
  variant='subtle',
  color='goldenrod',
  id='color-scheme-toggle',
  size='lg',
)

@callback(
  Output('mantine-provider', 'forceColorScheme'),
  Output('theme-store', 'data'),
  Input('color-scheme-toggle', 'n_clicks'),
  Input('theme-store', 'data'),
  prevent_initial_call=False,  # allow initialization on page load
)
def update_theme(n_clicks, stored_theme):
  # determine the trigger from ctx
  if ctx.triggered_id == 'theme-store':
    # loading the page: init from local storage
    return stored_theme or 'light', stored_theme or 'light'
  elif ctx.triggered_id == 'color-scheme-toggle':
    # the toggle button was clicked: toggle theme
    current_theme = stored_theme or 'light'
    new_theme = 'dark' if current_theme == 'light' else 'light'
    return new_theme, new_theme