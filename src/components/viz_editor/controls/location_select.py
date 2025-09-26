# from pathlib import Path

import dash_mantine_components as dmc

# import pandas as pd

# BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# path = BASE_DIR / 'data' / 'metadata' / 'locations.csv'

# locations = pd.read_csv(path)
# location_records = locations.to_dict('records')
# options = [location['location_name'] for location in location_records]

# Temporarily use hardcoded values to test if CSV loading is causing the React child error
options = [
  'US',
  'Alabama',
  'Alaska',
  'Arizona',
  'Arkansas',
  'California',
  'Colorado',
  'Connecticut',
  'Delaware',
  'Florida',
  'Georgia',
  'Hawaii',
  'Idaho',
  'Illinois',
  'Indiana',
  'Iowa',
  'Kansas',
  'Kentucky',
  'Louisiana',
  'Maine',
  'Maryland',
  'Massachusetts',
  'Michigan',
  'Minnesota',
  'Mississippi',
  'Missouri',
  'Montana',
  'Nebraska',
  'Nevada',
  'New Hampshire',
  'New Jersey',
  'New Mexico',
  'New York',
  'North Carolina',
  'North Dakota',
  'Ohio',
  'Oklahoma',
  'Oregon',
  'Pennsylvania',
  'Rhode Island',
  'South Carolina',
  'South Dakota',
  'Tennessee',
  'Texas',
  'Utah',
  'Vermont',
  'Virginia',
  'Washington',
  'West Virginia',
  'Wisconsin',
  'Wyoming',
]


def location_select(value='US'):
  return dmc.Select(
    label='Location',
    placeholder='',
    id='location-select',
    value=value,
    data=options,
  )
