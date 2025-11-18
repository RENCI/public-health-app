import dash_mantine_components as dmc

from src.util.constants import get_unique_model_names

options = get_unique_model_names()


def models_select(value: list[str] = ['Ensemble'], disabled=False):
  return dmc.MultiSelect(
    label='Models',
    placeholder='',
    id='models-select',
    value=value,
    required=True,
    data=options,
    disabled=disabled,
  )
