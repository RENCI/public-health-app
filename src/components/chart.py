from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.components.enums import AgeGroup, Target
from src.constants import get_location_data, get_model_color, get_model_name, get_scenario_name

DATA_BASE_PATH = "src/data/data"


class Scenario:
  def __init__(self, scenario_id: int):
    self.id = scenario_id
    self.name = get_scenario_name(scenario_id)
    self.variables = [""]  # TODO: add variables

  def __str__(self):
    return f"{self.name}"


class Model:
  def __init__(self, model_id: int):
    self.id = model_id
    self.name = get_model_name(model_id)
    self.color = get_model_color(model_id)

  def __str__(self):
    return f"{self.name}"


class Location:
  def __init__(self, location: str):
    self.name = location.lower().capitalize()
    location_data = get_location_data(self.name)
    self.short_code = location_data[0]
    self.index = location_data[1]
    self.population = location_data[2]

  def __str__(self):
    return f"{self.name}"


class Annotation:
  def __init__(self, value: float, label: str, color: str):
    self.value = value
    self.label = label
    self.color = color


class ChartTitle:
  def __init__(
    self,
    pathogen: str,
    scenario: Scenario,
    models: list[Model],
    location: Location,
    age_group: AgeGroup | None,
  ):
    self.pathogen = pathogen
    self.scenario = scenario
    self.location = location
    self.age_group = age_group
    if not age_group:
      self.age_group = AgeGroup.ALL

  def __str__(self):
    return (
      f"{self.pathogen} Scenario {self.scenario}"
      + f"{(self.age_group.display_value + ' ') if self.age_group else ''} in {self.location}"
    )


class ChartControls:
  def __init__(
    self,
    x_axis: str,
    y_axis: str,
    round_num: int,
    pathogen: str,
    scenario_id: int,
    type_id: int,
    model_ids: list[int],
    location_name: str,
    target: str,
    age_group: str | None = None,
    annotations: list[dict[str, Any]] | None = None,
    uncertainty: str | None = None,
  ):
    self.x_axis = x_axis
    self.y_axis = y_axis
    self.round_num = round_num
    self.pathogen = pathogen
    self.scenario = Scenario(scenario_id)
    self.type_id = type_id
    self.models = [Model(model_id) for model_id in model_ids]
    self.location = Location(location_name)
    self.target = Target(target)
    self.age_group = AgeGroup.from_input_value(age_group) if age_group else None
    self.annotations = (
      [Annotation(**annotation) for annotation in annotations] if annotations else []
    )
    self.uncertainty = int(uncertainty.strip("%")) if uncertainty else None


class Chart:
  def __init__(self, controls: ChartControls):
    self.controls = controls

    self.title = ChartTitle(
      controls.pathogen,
      controls.scenario,
      controls.models,
      controls.location,
      controls.age_group,
    )

    self.refresh_fig()

  def refresh_fig(self) -> go.Figure:
    self._data = pd.read_parquet(self._get_file_path(), engine="pyarrow")
    self._data = self._data.set_index(self.controls.x_axis)
    self._data = self._data.query("scenario_id == @self.controls.scenario.id")
    self._data = self._data.query("type_id == @self.controls.type_id")
    self._data = self._data.query("model_name.isin([model.name for model in self.controls.models])")
    if self.controls.age_group:
      self._data = self._data.query("age_group == @self.controls.age_group.value")
    else:
      self._data = self._data.query("age_group == '0-130'")  # default to all ages
    self._data = self._data.sort_values(by=self.controls.x_axis)
    self._fig = px.line(self._data, y="value")
    if self.controls.annotations:
      for annotation in self.controls.annotations:
        self._fig.add_annotation(
          x=annotation.value,
          y=annotation.value,
          text=annotation.label,
          showarrow=False,
          font=dict(color=annotation.color),
        )
    return self._fig

  def get_controls(self) -> ChartControls:
    return self.controls

  def get_fig(self) -> go.Figure:
    return self._fig

  def get_data(self) -> pd.DataFrame:
    return self._data

  def _get_file_path(self) -> str:
    base_filename = (
      f"{DATA_BASE_PATH}/round{self.controls.round_num}/"
      + f"{self.controls.target.value}/{self.controls.location.name}"
    )
    filename = base_filename + "/sample/part-0.parquet"
    if not Path(filename).exists():
      filename = base_filename + "/quartile/part-0.csv"
    if not Path(filename).exists():
      raise FileNotFoundError(f"File not found for chart: {self.controls}")
    return filename
