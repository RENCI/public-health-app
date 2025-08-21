from dash import (
    callback,
    ctx,
    dcc,
    exceptions,
    html,
    Input,
    no_update,
    Output,
    register_page,
    State,
)
import dash_mantine_components as dmc
from urllib.parse import parse_qs
from dash_iconify import DashIconify
from src.data.insights import get_insight
from src.data.templates import templates
from src.components.explorer import save_button, visualization_editor
from src.util.get_query_param import get_query_param

register_page(__name__, path_template="/explorer", name="Insight Explorer")

back_button = dmc.Anchor("← Abandon Changes", href="/", id="back-button")

reset_button = dcc.Link(
    dmc.Button(
        "Reset to Original",
        leftSection=DashIconify(icon="feather:refresh-ccw"),
        variant="outline",
    ),
    id="reset-button",
    href="#",
)

toolbar = dmc.Flex(
    children=[back_button, dmc.Group([reset_button, save_button])],
    justify="space-between",
    align="center",
    mb=24,
)


def layout(starter=None):
    item = get_insight(starter) or {}
    details = item.get("details", "")
    title = item.get("title", "")
    overview = item.get("overview", "")

    return dmc.Container(
        [
            toolbar,
            visualization_editor(),
        ],
        fluid=True,
    )


@callback(
    Output("back-button", "href"),
    Input("url", "search"),
)
def update_back_button_href(search):
    starter = get_query_param(search, "starter")
    if not starter:
        raise exceptions.PreventUpdate
    return f"/viewer?id={starter}" if starter else "/"
