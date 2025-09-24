import dash_mantine_components as dmc

from src.constants import get_model_names

models = [model_name for model_name in get_model_names()]
options = [{'value': m, 'label': m} for m in models]


def models_select(value=['Ensemble_LOP']):
  return dmc.MultiSelect(
    label='Models',
    placeholder='',
    id='models-select',
    value=value,
    data=options,
  )
