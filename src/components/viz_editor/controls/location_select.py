from pathlib import Path

import dash_mantine_components as dmc
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

path = BASE_DIR / 'data' / 'metadata' / 'locations.csv'

locations = pd.read_csv(path)
location_records = locations.to_dict('records')
options = [
  {'value': location['location_name'], 'label': location['location_name']}
  for location in location_records
]


def location_select(value='US'):
  return dmc.Select(
    label='Location',
    placeholder='',
    id='location-select',
    value=value,
    required=True,
    data=options,
    comboboxProps={'shadow': 'md'},
  )
