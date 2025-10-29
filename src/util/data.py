import os
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent  # src
ROUNDS_DIR = os.path.join(BASE_DIR, 'data', 'rounds')


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
    round_date = dirname.replace('date', '')
    rounds_path = os.path.join(ROUNDS_DIR, dirname)
    details_path = os.path.join(rounds_path, 'details.yaml')
    insights_path = os.path.join(rounds_path, 'insights')

    details = {}
    if os.path.exists(details_path):
      with open(details_path, 'r') as f:
        details = yaml.safe_load(f) or {}

    insights = load_insights(insights_path)

    rounds[round_number] = dict(
      round_number=int(round_number),
      name=details.get('name'),
      date=details.get('date'),
      report=details.get('report', ''),
      insights=insights,
      methods=details.get('methods', ''),
    )

  return rounds
