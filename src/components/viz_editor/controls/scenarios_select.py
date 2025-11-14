import dash_mantine_components as dmc

from src.constants import get_scenario_names

options = [s for s in get_scenario_names()]


def scenarios_select(value: list[str] = []):
  return dmc.MultiSelect(
    label='Scenarios',
    placeholder='',
    id='scenarios-select',
    value=value,
    required=True,
    data=options,
  )
