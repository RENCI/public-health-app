from datetime import datetime
from typing import Any

from src.components.chart.chart_properties import (
  Annotation,
  Location,
  Model,
  PlotType,
  Scenario,
  Zoom,
)
from src.components.enums import AgeGroup, CertaintyInterval, DataType, Target


class ChartControls:
  def __init__(
    self,
    plot_type: str,
    round_num: int,
    scenario_names: list[str],
    model_names: list[str],
    location_name: str,
    target: str,
    age_group: str,
    x_axis: str,
    y_axis: str,
    x_start_date: str | None = None,
    zoom: dict[str, dict[str, Any]] | None = None,
    annotations: list[dict[str, Any]] | None = None,
    certainty_percent: str | None = None,
    pathogen: str = 'covid',
  ):
    self.plot_type = PlotType(plot_type)
    self.round_num = round_num
    self.pathogen = pathogen
    self.scenarios = [Scenario(name=scenario_name) for scenario_name in scenario_names]
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
    self.zoom = Zoom(x=zoom['x'], y=zoom['y']) if zoom else Zoom()
    self.data_type = DataType.QUANTILE
