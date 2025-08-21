import json
from dash import callback, dcc, Input, Output, State, html
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from .controls import controls
import pandas as pd

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

with open("src/config/constant.json", "r") as f:
    constants = json.load(f)
with open("src/config/viz_settings.json", "r") as f:
    viz_settings = json.load(f)

df = pd.read_csv("src/assets/round1/cum-hosp/California/quantile/part-0.csv")
df = df.set_index("target_end_date")
df = df[(df["scenario_id"] == 2)]
df = df[df["type_id"] == 0.5]
df = df[df["model_name"] == 1]
df = df[df["age_group"] == "0-130"]

title = (
    constants["pathogen_display_name"]
    + " Scenario "
    + constants["scenario_id"]["1"]
    + " using "
    + constants["model_name"]["1"]
    + " model, for "
    + viz_settings["Round 1 - 2023/2024"]["age_group"]["0-130"]
)


def visualization_editor():
    return dmc.Grid(
        children=[
            dmc.GridCol(
                html.Div(
                    [
                        dmc.Title(title, order=1),
                        dmc.LineChart(
                            h=300,
                            dataKey="target_end_date",
                            data=df.to_dict(orient="records"),
                            tickLine="xy",
                            yAxisProps={"tickMargin": 15, "orientation": "right"},
                            xAxisProps={"tickMargin": 15, "orientation": "top"},
                            series=[
                                {
                                    "name": "value",
                                    "label": "Cumulative Hospitalizations",
                                    "color": "indigo.6",
                                },
                            ],
                        ),
                    ]
                ),
                id="visualization-column",
                span=8,
            ),
            dmc.GridCol(
                controls,
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
                span=dict(base=12),
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
