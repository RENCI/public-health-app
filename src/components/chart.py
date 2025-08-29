import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.components.enums import AgeGroup, Target

DATA_BASE_PATH = "src/data/data"


class ChartTitle:
  def __init__(
    self, pathogen: str, scenario: int, model: int, location: str, age_group: AgeGroup | None
  ):
    self.pathogen = pathogen
    self.scenario = scenario
    self.model = model
    self.location = location
    self.age_group = age_group

  def __str__(self):
    return (
      f"{self.pathogen} Scenario {self.scenario} using {self.model} model, "
      + f"{(self.age_group.display_value + ' ') if self.age_group else ''}in {self.location}"
    )


class ChartControls:
  def __init__(
    self,
    x_axis: str,
    y_axis: str,
    round_num: int,
    pathogen: str,
    scenario: int,
    type_id: int,
    model: int,
    location: str,
    age_group: AgeGroup,
    target: Target,
  ):
    self.x_axis = x_axis
    self.y_axis = y_axis
    self.round_num = round_num
    self.pathogen = pathogen
    self.scenario = scenario
    self.type_id = type_id
    self.model = model
    self.location = location
    self.age_group = age_group
    self.target = target


class Chart:
  def __init__(self, controls: ChartControls):
    self.controls = controls
    self.controls.location = controls.location.lower().capitalize()

    self.title = ChartTitle(
      controls.pathogen, controls.scenario, controls.model, controls.location, controls.age_group
    )

    self.refresh_fig()

  def refresh_fig(self) -> go.Figure:
    self._data = pd.read_parquet(self._get_file_path(), engine="pyarrow")
    self._data = self._data.set_index(self.controls.x_axis)
    self._data = self._data.query("scenario_id == @self.controls.scenario")
    self._data = self._data.query("type_id == @self.controls.type_id")
    self._data = self._data.query("model_name == @self.controls.model")
    # self._data = self._data.query("age_group == @self.controls.age_group.value")
    self._data = self._data.sort_values(by=self.controls.x_axis)
    self._fig = px.line(self._data, y="value")
    return self._fig

  def get_controls(self) -> ChartControls:
    return self.controls

  def get_fig(self) -> go.Figure:
    return self._fig

  def get_data(self) -> pd.DataFrame:
    return self._data

  def _get_file_path(self) -> str:
    return (
      f"{DATA_BASE_PATH}/{self.controls.pathogen}/round{self.controls.round_num}/"
      + f"{self.controls.target.value}/{self.controls.location}/"
      + "sample/part-0.parquet"
    )
