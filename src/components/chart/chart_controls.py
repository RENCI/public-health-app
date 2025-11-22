from src.components.chart.chart_properties import (
  Annotation,
  Location,
  Model,
  PlotType,
  Scenario,
  ScenarioVariable,
  Zoom,
)
from src.components.enums import AgeGroup, DataType, Target, UncertaintyInterval


class ChartControls:
  def __init__(
    self,
    theme: str,
    plot_type: str,
    round_num: int,
    scenario_ids: list[int],
    scenario_variables: list[dict],
    model_names: list[str],
    location_name: str,
    target: str,
    age_group: str,
    x_axis: str | None = None,
    y_axis: str | None = None,
    columns: int = 1,
    zoom: dict | None = None,
    annotations: list[dict] | None = None,
    uncertainty_interval: str | None = None,
    pathogen: str = 'covid',
  ):
    self.theme = theme
    self.plot_type = PlotType(plot_type)
    self.round_num = round_num
    self.pathogen = pathogen
    self.scenarios = [Scenario(id=scenario_id) for scenario_id in scenario_ids]
    self.scenario_variables = [ScenarioVariable(**var) for var in scenario_variables]
    self.models = [Model(model_name) for model_name in model_names]
    self.location = Location(location_name)
    self.target = Target.from_input_value(target)
    self.age_group = AgeGroup.from_input_value(age_group)
    self.x_axis = x_axis
    self.y_axis = y_axis
    self.columns = columns
    self.annotations = (
      [Annotation.from_dict(annotation) for annotation in annotations] if annotations else None
    )
    self.uncertainty_interval = (
      UncertaintyInterval.from_display_value(uncertainty_interval) if uncertainty_interval else None
    )
    if zoom is not None:
      self.zoom = Zoom(**zoom)
    else:
      self.zoom = None
    self.data_type = DataType.QUANTILE

  @classmethod
  def from_dict(cls, data: dict):
    return cls(
      theme=data['theme'],
      plot_type=data['plot_type'],
      round_num=data['round_num'],
      scenario_ids=data['scenario_ids'],
      scenario_variables=data['scenario_variables'],
      model_names=data['model_names'],
      location_name=data['location_name'],
      target=data['target'],
      age_group=data['age_group'],
      x_axis=data['x_axis'],
      y_axis=data['y_axis'],
      columns=data.get('columns', 1),
      zoom=data.get('zoom', None),
      annotations=data.get('annotations', None),
      uncertainty_interval=data.get('uncertainty_interval', None),
    )
