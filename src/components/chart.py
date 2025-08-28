import pandas as pd
from src.components.enums import AgeGroupInput, AgeGroup
import plotly.express as px

DATA_BASE_PATH = "src/data/data"

class ChartTitle:

  def __init__(
    self,
    pathogen: str,
    scenario: str,
    model: str,
    location: str,
    age_group: AgeGroup
  ):
    self.pathogen = pathogen
    self.scenario = scenario
    self.model = model
    self.location = location
    self.age_group = age_group

  def __str__(self):
    return f"{self.pathogen} Scenario {self.scenario} using {self.model} model, for " + \
      f"{self.age_group.value} and in {self.location}"
  
class ChartControls:

  def __init__(
    self,
    round_num: int,
    pathogen: str,
    scenario: str,
    model: str,
    location: str,
    age_group: AgeGroupInput,
    target: str
  ):
    self.round_num = round_num
    self.pathogen = pathogen
    self.scenario = scenario
    self.model = model
    self.location = location
    self.age_group = age_group
    self.target = target

class Chart:

  def __init__(
    self,
    controls: ChartControls
  ):
    self.controls = controls
    self.controls.location = controls.location.lower().capitalize()
    self.controls.age_group = AgeGroup("all ages")

    self.title = ChartTitle(controls.pathogen, controls.scenario, controls.model, controls.location, controls.age_group)

    file_path = f"{DATA_BASE_PATH}/{controls.pathogen}/round{controls.round_num}/" + \
      f"{controls.target.value}/{controls.location}/" + \
      f"sample/part-0.parquet"
    self.data = pd.read_parquet(file_path, engine='pyarrow')

    self.fig = px.line(self.data, x="target_end_date", y="value")
