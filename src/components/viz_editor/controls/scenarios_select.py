import dash_mantine_components as dmc
from dash import Input, Output, callback

from src.util.constants import get_scenarios_for_round

scenarios = get_scenarios_for_round(19)
options = [
  {
    'label': f'{str(scenario["name"]).split("-")[0]}. {scenario["description"]}',
    'value': str(scenario['id']),
  }
  for scenario in scenarios
]
default_option = [options[0]['value']] if options else None


def scenarios_select(value: list[str] = default_option):
  return dmc.MultiSelect(
    label='Scenarios',
    placeholder='',
    id='scenarios-select',
    value=value,
    required=True,
    data=options,
    comboboxProps={'shadow': 'md'},
  )


@callback(
  Output('scenarios-select', 'value', allow_duplicate=True),
  Input('scenarios-select', 'value'),
  prevent_initial_call=True,
)
def on_scenarios_select_change(selected_values: list[str]):
  if not selected_values:
    return []

  # Keep selected values sorted for consistency
  selected_values.sort()
  return selected_values


@callback(
  Output('scenarios-select', 'data'),
  Output('scenarios-select', 'value', allow_duplicate=True),
  Input('selected-round-store', 'data'),
  prevent_initial_call=True,
)
def update_scenarios_select_for_round(round_number: str):
  if not round_number:
    return [], None
  scenarios = get_scenarios_for_round(int(round_number))
  options = [
    {
      'label': f'{str(scenario["name"]).split("-")[0]}. {scenario["description"]}',
      'value': str(scenario['id']),
    }
    for scenario in scenarios
  ]
  first_scenario_value = options[0]['value'] if options else None
  return options, [first_scenario_value] if first_scenario_value else None
