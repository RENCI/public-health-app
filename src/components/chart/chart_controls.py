from src.components.chart.chart_properties import (
  Annotation,
  Location,
  Model,
  PlotType,
  Scenario,
  ScenarioVariable,
  Zoom,
)
from src.components.enums import AgeGroup, Target, UncertaintyInterval

DEFAULT_CONTROL_VALUES = {
  'theme': 'light',
  'plot_type': 'line',
  'round_num': 19,
  'scenario_ids': [77, 78],
  'scenario_variables': [
    {
      'name': 'Vaccination Strategy',
      'options': ['High risk', 'All ages'],
      'selected_option': 'All ages',
    }
  ],
  'model_names': ['Ensemble'],
  'location_name': 'US',
  'target': 'incident_hospitalization',
  'age_group': '0-130',
  'x_axis': 'target_end_date',
  'y_axis': 'value',
  'zoom': None,
  'annotations': None,
  'uncertainty_interval': 'None',
}


class ChartControls:
  theme: str
  plot_type: PlotType
  round_num: int
  scenarios: list[Scenario]
  scenario_variables: list[ScenarioVariable]
  models: list[Model]
  location: Location
  target: Target
  age_group: AgeGroup
  x_axis: str
  y_axis: str
  columns: int
  annotations: list[Annotation] | None
  uncertainty_interval: UncertaintyInterval | None
  saved_zoom: Zoom | None
  current_zoom: Zoom | None

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
    saved_zoom: dict | None = DEFAULT_CONTROL_VALUES['zoom'],
    current_zoom: dict | None = None,
    annotations: list[dict] | None = DEFAULT_CONTROL_VALUES['annotations'],
    uncertainty_interval: str = DEFAULT_CONTROL_VALUES['uncertainty_interval'],
  ):
    self.theme = theme
    self.plot_type = PlotType(plot_type)
    self.round_num = round_num
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
    # If saved_zoom or current_zoom is provided, initialize with it, otherwise set both to None
    self.saved_zoom = Zoom.from_dict(saved_zoom) if saved_zoom else None
    self.current_zoom = Zoom.from_dict(current_zoom) if current_zoom else None

  @classmethod
  def from_dict(cls, data: dict):
    controls = cls(
      theme=data.get('theme', DEFAULT_CONTROL_VALUES['theme']),
      plot_type=data.get('plot_type', DEFAULT_CONTROL_VALUES['plot_type']),
      round_num=data.get('round_num', DEFAULT_CONTROL_VALUES['round_num']),
      scenario_ids=data.get('scenario_ids', DEFAULT_CONTROL_VALUES['scenario_ids']),
      scenario_variables=data.get(
        'scenario_variables', DEFAULT_CONTROL_VALUES['scenario_variables']
      ),
      model_names=data.get('model_names', DEFAULT_CONTROL_VALUES['model_names']),
      location_name=data.get('location_name', DEFAULT_CONTROL_VALUES['location_name']),
      target=data.get('target', DEFAULT_CONTROL_VALUES['target']),
      age_group=data.get('age_group', DEFAULT_CONTROL_VALUES['age_group']),
      x_axis=data.get('x_axis', DEFAULT_CONTROL_VALUES.get('x_axis')),
      y_axis=data.get('y_axis', DEFAULT_CONTROL_VALUES.get('y_axis')),
      saved_zoom=data.get('zoom', DEFAULT_CONTROL_VALUES['zoom']),
      current_zoom=data.get('current_zoom', None),
      annotations=data.get('annotations', DEFAULT_CONTROL_VALUES['annotations']),
      uncertainty_interval=data.get(
        'uncertainty_interval', DEFAULT_CONTROL_VALUES['uncertainty_interval']
      ),
    )
    return controls
