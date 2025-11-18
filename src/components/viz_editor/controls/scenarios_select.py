import dash_mantine_components as dmc
from dash import Input, Output, callback

from src.util.constants import get_scenarios_for_round

scenarios = get_scenarios_for_round(19)
options = [
  {'label': scenario['description'], 'value': str(scenario['id'])} for scenario in scenarios
]
default_option = [int(option['value']) for option in options] if options else []


def scenarios_select(value: list[int] = default_option):
  return dmc.MultiSelect(
    label='Scenarios',
    placeholder='',
    id='scenarios-select',
    value=value,
    required=True,
    data=options,
  )


@callback(
  Output('scenarios-select', 'data'),
  Output('scenarios-select', 'value'),
  Input('selected-round-store', 'data'),
  prevent_initial_call=True,
)
def update_scenarios_select_for_round(round_number: str):
  if not round_number:
    return [], None
  scenarios = get_scenarios_for_round(int(round_number))
  options = [
    {'label': scenario['description'], 'value': str(scenario['id'])} for scenario in scenarios
  ]
  first_scenario_value = [int(option['value']) for option in options] if options else None
  return options, [first_scenario_value] if first_scenario_value else None
