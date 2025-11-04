import dash_mantine_components as dmc

from src.constants import get_model_names

options = [m for m in get_model_names()]


def models_select(value=['Ensemble']):
  return dmc.MultiSelect(
    label='Models',
    placeholder='',
    id='models-select',
    value=value,
    required=True,
    data=options,
  )
