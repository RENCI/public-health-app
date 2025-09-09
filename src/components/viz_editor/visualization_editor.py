import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, dcc, html
from dash_iconify import DashIconify

from src.components.chart import Chart, ChartControls
from src.util.data import build_dataset_path, collect_data

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

default_control_values = dict(
  location="US",
  target="incident_hospitalization",
  age_group="All Ages",
  uncertainty="None",
  ensemble="Ensemble",
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


def visualization_editor(control_values=None, show_controls=True):
  controls = {**default_control_values, **(control_values or {})}

  init_location = controls["location"]
  init_target = controls["target"]
  init_age_group = controls["age_group"]
  init_uncertainty = controls["uncertainty"]
  init_ensemble = controls["ensemble"]

  if not show_controls:
    init_data = collect_data(build_dataset_path(location=init_location, target=init_target))
    current_data_store = dcc.Store(id="current-data-store", data=init_data)
  else:
    current_data_store = dcc.Store(id="current-data-store", data=[])

  chart = Chart(
    ChartControls(
      x_axis="horizon",
      y_axis="value",
      round_num=round_nums[0],
      pathogen=pathogens[0],
      scenario=controls["scenario"],
      type_id=controls["type_id"],
      model=controls["model"],
      location=controls["location"],
      age_group=controls["age_group"],
      target=controls["target"],
    )
  )

  figure_container = html.Div(
    id="insight-visualization-figure",
    children=dmc.Skeleton(height=500, w="100%"),
  )

  if not show_controls:
    return dmc.Container(
      [
        current_data_store,
        figure_container,
      ]
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
                span=dict(base=12),
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
                age_group_select(value=init_age_group),
                style=dict(padding="var(--mantine-spacing-sm)"),
                span=dict(base=12),
              ),
              dmc.GridCol(
                uncertainty_select(value=init_uncertainty),
                style=dict(padding="var(--mantine-spacing-sm)"),
                span=dict(base=12),
              ),
              dmc.GridCol(
                ensemble_select(value=init_ensemble),
                style=dict(padding="var(--mantine-spacing-sm)"),
                span=dict(base=12),
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


# only makes sense in explorer
@callback(
  Output("current-data-store", "data", allow_duplicate=True),
  Input("location-select", "value"),
  Input("target-select", "value"),
  prevent_initial_call="initial_duplicate",
)
def get_data(location, target):
  path = build_dataset_path(location=location, target=target)
  return collect_data(path)


# fires in both explorer and viewer "modes"
@callback(
  Output("insight-visualization-figure", "children"),
  Input("current-data-store", "data"),
)
def update_chart(data):
  if not data:
    return dmc.Image(src="https://placehold.co/1200x400?text=Not found")

  # convert list of dicts back to DataFrame for convenience
  df = pd.DataFrame(data)

  fig = px.line(
    df, x="target_end_date", y="value", color="scenario_id", title="Forecast values over time"
  )
  return dcc.Graph(figure=fig)
