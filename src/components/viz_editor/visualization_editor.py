import dash_mantine_components as dmc
from dash import Input, Output, State, callback, dcc, html
from dash_iconify import DashIconify

from src.components.chart import Chart, ChartControls
from src.components.enums import AgeGroup, Target

from .controls.age_group_select import age_group_select
from .controls.ensemble_select import ensemble_select
from .controls.location_select import location_select
from .controls.scenarios_select import scenarios_select
from .controls.target_select import target_select
from .controls.uncertainty_select import uncertainty_select

controls_visibility_store = dcc.Store(
  id="controls-visibility", data=True
)  # True = open, False = closed

controls_toggle = dmc.Button(
  "Hide Controls",
  rightSection=DashIconify(icon="feather:chevron-right"),
  id="controls-toggle",
  variant="subtle",
  size="xs",
)

round_nums = [1, 2]
scenarios = ["1", "2"]
pathogens = ["covid-19", "rsv"]
locations = ["California", "Colorado"]
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
  "Ensemble_LOP_all",
]


def visualization_editor(controls={}):
  init_location: str = controls.get("location", "California")
  init_target: str = controls.get("target", "inc hosp")

  chart = Chart(
    ChartControls(
      x_axis="horizon",
      y_axis="value",
      round_num=round_nums[0],
      pathogen=pathogens[0],
      scenario=66,
      type_id=66,
      model=1,
      location=locations[0],
      age_group=AgeGroup.from_input_value(controls.get("age_group", "0-130")),
      target=Target(init_target.lower()),
    )
  )

  return dmc.Grid(
    children=[
      dmc.GridCol(
        html.Div(
          [
            dmc.Title(str(chart.title), order=1),
            dcc.Graph(
              id="insight-visualization",
              figure=chart.get_fig(),
            ),
          ]
        ),
        id="visualization-column",
        span=8,
      ),
      dmc.GridCol(
        dmc.Card(
          dmc.Grid(
            children=[
              dmc.GridCol(
                scenarios_select,
                style=dict(padding="var(--mantine-spacing-sm)"),
                span=12,
              ),
              dmc.GridCol(
                location_select(value=init_location),
                style=dict(padding="var(--mantine-spacing-sm)"),
                span=12,
              ),
              dmc.GridCol(
                target_select(value=init_target),
                style=dict(padding="var(--mantine-spacing-sm)"),
                span=12,
              ),
              dmc.GridCol(
                age_group_select,
                style=dict(padding="var(--mantine-spacing-sm)"),
                span=12,
              ),
              dmc.GridCol(
                uncertainty_select,
                style=dict(padding="var(--mantine-spacing-sm)"),
                span=12,
              ),
              dmc.GridCol(
                ensemble_select, style=dict(padding="var(--mantine-spacing-sm)"), span=12
              ),
            ],
            gutter=0,
          ),
          variant="soft",
          style=dict(height="100%"),
        ),
        id="controls-column",
        span=4,
      ),
      dmc.GridCol(
        [
          controls_visibility_store,
          dmc.ButtonGroup(
            [
              controls_toggle,
            ],
            style=dict(justifyContent="flex-end"),
          ),
        ],
        span=12,
      ),
    ],
    mb=12,
  )


# toggle the controls visibility store value when clicking the button
@callback(
  Output("controls-visibility", "data"),
  Output("controls-toggle", "children"),
  Output("controls-toggle", "rightSection"),
  Input("controls-toggle", "n_clicks"),
  State("controls-visibility", "data"),
  prevent_initial_call=True,
)
def toggle_controls_visibility_store(n_clicks, is_open):
  new_open = not is_open
  new_label = "Hide Controls" if new_open else "Show Controls"
  new_icon = (
    DashIconify(icon="feather:chevron-right")
    if new_open
    else DashIconify(icon="feather:chevron-left")
  )
  return new_open, new_label, new_icon


# update layout based on store value
@callback(
  Output("visualization-column", "span"),
  Output("controls-column", "span"),
  Output("controls-column", "style"),
  Input("controls-visibility", "data"),
)
def update_sidebar_display(is_open):
  if is_open:
    return 8, 4, {}
  else:
    return 12, 0, {"display": "none"}
