from datetime import datetime

from src.components.chart.chart_properties import (
  Annotation,
  AxisRange,
  Location,
  Model,
  PlotType,
  Scenario,
  ScenarioVariable,
  Zoom,
)
from src.components.enums import AgeGroup, CertaintyInterval, DataType, Target


class ChartControls:
  def __init__(
    self,
    plot_type: str,
    round_num: int,
    scenario_names: list[str],
    scenario_variables: list[dict],
    model_names: list[str],
    location_name: str,
    target: str,
    age_group: str,
    x_axis: str | None = None,
    y_axis: str | None = None,
    x_start_date: str | None = None,
    zoom: dict | None = None,
    annotations: list[dict] | None = None,
    certainty_percent: str | None = None,
    pathogen: str = 'covid',
  ):
    self.plot_type = PlotType(plot_type)
    self.round_num = round_num
    self.pathogen = pathogen
    self.scenarios = [Scenario(name=scenario_name) for scenario_name in scenario_names]
    self.scenario_variables = [ScenarioVariable(**var) for var in scenario_variables]
    self.models = [Model(model_name) for model_name in model_names]
    self.location = Location(location_name)
    self.target = Target.from_input_value(target)
    self.age_group = AgeGroup.from_input_value(age_group)
    self.x_axis = x_axis
    self.y_axis = y_axis
    self.x_start_date = datetime.strptime(x_start_date, '%Y-%m-%d') if x_start_date else None
    self.annotations = (
      [Annotation.from_dict(annotation) for annotation in annotations] if annotations else None
    )
    self.certainty_percent = (
      CertaintyInterval.from_display_value(certainty_percent) if certainty_percent else None
    )
    if zoom is not None:
      self.zoom = Zoom(**zoom)
    else:
      self.zoom = None
    self.data_type = DataType.QUANTILE

  @classmethod
  def from_dict(cls, data: dict):
    return cls(
      plot_type=data['plot_type'],
      round_num=data['round_num'],
      scenario_names=data['scenario_names'],
      scenario_variables=data['scenario_variables'],
      model_names=data['model_names'],
      location_name=data['location_name'],
      target=data['target'],
      age_group=data['age_group'],
      x_axis=data['x_axis'],
      y_axis=data['y_axis'],
      x_start_date=data['x_start_date'],
      zoom=data.get('zoom', None),
      annotations=data.get('annotations', None),
      certainty_percent=data.get('certainty_percent', None),
    )
