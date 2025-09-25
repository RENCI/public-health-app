import dash_mantine_components as dmc

from src.constants import get_scenario_names

scenarios = get_scenario_names()
options = [{'value': c, 'label': c} for c in scenarios]


def scenarios_select(value: list[str] = scenarios):
  return dmc.MultiSelect(
    label='Scenarios',
    placeholder='',
    id='scenarios-select',
    value=value,
    data=options,
  )
