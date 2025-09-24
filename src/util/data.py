import os
import yaml
from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent  # src
ROUNDS_DIR = os.path.join(BASE_DIR, 'data', 'rounds')


def build_dataset_path(
  *,
  pathogen: str = 'flu',
  round_number: int = 1,
  location: str = 'US',
  target: str = 'incident_hospitalization',
  part: int = 0,
) -> Path:
  pathogen = str(pathogen or 'flu')
  round_number = str(round_number or 1)
  location = str(location or 'US')
  target = str(target or 'incident_hospitalization')
  part = str(part or 0)
  path = (
    BASE_DIR
    / 'data'
    / 'rounds'
    / f'round{round_number}'
    / target
    / location
    / 'quantile'
    / f'part-{part}.csv'
  )
  return path


def collect_data(path):
  path = Path(path)

  if not path.exists() or not path.is_file():
    print(f'Error: File not found at "{path}"')
    return None

  try:
    df = pd.read_csv(path)
    return df.to_dict('records')
  except Exception as e:
    print(f'Error reading file "{path}": {e}')
    return None


def load_insights(path):
  """Load all YAML insight files from a given path."""
  insights = []
  if not os.path.exists(path):
    return insights

  for filename in sorted(os.listdir(path)):
    if filename.endswith('.yaml'):
      filepath = os.path.join(path, filename)
      with open(filepath, 'r') as f:
        insight = yaml.safe_load(f)
        insight['type'] = 'system'
        insights.append(insight)

  insights.sort(key=lambda x: x.get('title', '').lower())
  return insights


def load_rounds():
  """Return dict of rounds, with its details and insights"""
  rounds = {}

  for dirname in sorted(os.listdir(ROUNDS_DIR)):
    if not dirname.startswith('round'):
      continue

    round_number = dirname.replace('round', '')
    round_path = os.path.join(ROUNDS_DIR, dirname)
    details_path = os.path.join(round_path, 'details.yaml')
    insights_path = os.path.join(round_path, 'insights')

    details = {}
    if os.path.exists(details_path):
      with open(details_path, 'r') as f:
        details = yaml.safe_load(f) or {}

    insights = load_insights(insights_path)

    rounds[round_number] = dict(
      round_number=int(round_number),
      name=f'Round {round_number}',
      report=details.get('report', ''),
      insights=insights,
    )

  return rounds

  # rounds = {}
  # for round_dir in sorted(os.listdir(ROUNDS_DIR)):
  #   full_path = os.path.join(ROUNDS_DIR, round_dir)
  #   if not os.path.isdir(full_path) or not round_dir.lower().startswith('round'):
  #     continue

  #   # reduce key to just the number
  #   round_num = round_dir.lower().replace('round', '')

  #   insights = []
  #   for filename in sorted(os.listdir(full_path)):
  #     if filename.endswith('.yaml'):
  #       path = os.path.join(full_path, filename)
  #       with open(path, 'r') as f:
  #         insight = yaml.safe_load(f)
  #         insight['type'] = 'system'
  #         insights.append(insight)

  #   insights.sort(key=lambda x: x.get('title', '').lower())
  #   rounds[round_num] = insights

  # return rounds
