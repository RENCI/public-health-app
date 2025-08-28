from dash import callback, dcc, Input, Output, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from .controls.scenarios_select import scenarios_select
from .controls.location_select import location_select
from .controls.target_select import target_select
from .controls.age_group_select import age_group_select
from .controls.uncertainty_select import uncertainty_select
from .controls.ensemble_select import ensemble_select
from src.components.enums import Target, AgeGroupInput
from src.components.chart import Chart, ChartControls

controls_visibility_store = dcc.Store(id='controls-visibility', data=True)  # True = open, False = closed

controls_toggle = dmc.Button(
  'Hide Controls',
  rightSection=DashIconify(icon='feather:chevron-right'),
  id='controls-toggle',
  variant='subtle',
  size='xs',
)

round_nums = [1, 2]
pathogens = ["covid-19", "rsv"]
models = [
  "Ensemble_LOP_untrimmed",
  "Ensemble_LOP",
  "Ensemble",
  "UT-ImmunoSEIRS",
  "NotreDame-FRED",
  "USC-SIkJalpha",
  "CU-RSV_SVIRS",
  "UVA-EpiHiperRSV",
  "NIH-RSV_WIN",
  "PSI-PROF",
  "NIH-RSV_MSIRS",
  "MOBS_NEU-GLEAM_RSV",
  "NIH-RSV_Phenomenological",
  "CEPH-MetaRSV",
  "JHU_UNC-flepiMoP",
  "Ensemble_LOP_all"
],
chart = Chart(ChartControls(1, "covid-19", pathogens[0], models[0], "California", AgeGroupInput.ALL, Target.INCIDENT_HOSPITALIZATION))

def visualization_editor(controls={}):
  init_location = controls.get('location', 'US')
  init_target = controls.get('target', 'Incident Hospitalization')

  return dmc.Grid(
    children=[
      dmc.GridCol(
        dmc.Image(id='insight-visualization', src=chart.fig.to_image(format="png"), radius='sm'),
        id='visualization-column',
        span=8,
      ),
      dmc.GridCol(
        dmc.Card(
          dmc.Grid(
            children=[
              dmc.GridCol(scenarios_select,   style=dict(padding='var(--mantine-spacing-sm)'), span=dict(base=12)),
              dmc.GridCol(
                location_select(value=init_location),
                style=dict(padding='var(--mantine-spacing-sm)'),
                span=dict(base=12),
              ),
              dmc.GridCol(
                target_select(value=init_target),
                style=dict(padding='var(--mantine-spacing-sm)'),
                span=dict(base=12),
              ),
              dmc.GridCol(age_group_select,   style=dict(padding='var(--mantine-spacing-sm)'), span=dict(base=12)),
              dmc.GridCol(uncertainty_select, style=dict(padding='var(--mantine-spacing-sm)'), span=dict(base=12)),
              dmc.GridCol(ensemble_select,    style=dict(padding='var(--mantine-spacing-sm)'), span=dict(base=12)),
            ],
            gutter=0,
          ),
          variant='soft',
          style=dict(height='100%'),
        ),
        id='controls-column',
        span=4,
      ),
      dmc.GridCol(
        [
          controls_visibility_store,
          dmc.ButtonGroup([
            controls_toggle,
          ], style=dict(justifyContent='flex-end')),
        ],
        span=dict(base=12),
      ),
    ],
    mb=12,
  )

# toggle the controls visibility store value when clicking the button
@callback(
  Output('controls-visibility', 'data'),
  Output('controls-toggle', 'children'),
  Output('controls-toggle', 'rightSection'),
  Input('controls-toggle', 'n_clicks'),
  State('controls-visibility', 'data'),
  prevent_initial_call=True
)
def toggle_controls_visibility_store(n_clicks, is_open):
  new_open = not is_open
  new_label = 'Hide Controls' if new_open else 'Show Controls'
  new_icon = DashIconify(icon='feather:chevron-right') if new_open else DashIconify(icon='feather:chevron-left')
  return new_open, new_label, new_icon

# update layout based on store value
@callback(
  Output('visualization-column', 'span'),
  Output('controls-column', 'span'),
  Output('controls-column', 'style'),
  Input('controls-visibility', 'data'),
)
def update_sidebar_display(is_open):
  if is_open:
    return 8, 4, {}
  else: return 12, 0, {'display': 'none'}
