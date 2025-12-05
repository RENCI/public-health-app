import inspect
import os
from datetime import datetime
from pathlib import Path
from typing import Any

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
        insight = yaml.safe_load(f) or {}
        insight['type'] = 'system'
        insights.append(insight)

  # sort by `order`, then by `title`
  insights.sort(
    key=lambda x: (
      x.get('order', float('inf')),
      x.get('title', '').lower(),
    )
  )

  return insights


def load_rounds():
  """Return dict of rounds, with its details and insights"""
  rounds = {}

  for dirname in sorted(os.listdir(ROUNDS_DIR)):
    if not dirname.startswith('round'):
      continue

    round_number = dirname.replace('round', '')
    rounds_path = os.path.join(ROUNDS_DIR, dirname)
    details_path = os.path.join(rounds_path, 'details.yaml')
    insights_path = os.path.join(rounds_path, 'insights')

    details = {}
    if os.path.exists(details_path):
      with open(details_path, 'r') as f:
        details = yaml.safe_load(f) or {}

    insights = load_insights(insights_path)

    rounds[round_number] = {
      'round_number': int(round_number),
      'date': details.get('date'),
      'name': details.get('name'),
      'report': details.get('report', ''),
      'insights': insights,
      'methods': details.get('methods'),
    }

  return rounds


def all_not_none(*values: Any, log_result: bool = False) -> bool:
  """Check if all values are not None."""
  result = all(value is not None for value in values)
  print(f'all_not_none: {result}')
  if log_result:
    caller_frame = inspect.currentframe().f_back
    caller_locals = caller_frame.f_locals if caller_frame else {}

    for value in values:
      var_name = None
      for name, var_value in caller_locals.items():
        if var_value is None:
          var_name = name
          if var_name:
            print(f'{var_name} is None\n')
          else:
            print('Value is None\n')
          break
  return result


def any_are_none(*values: Any, log_result: bool = False) -> bool:
  """Check if any values are None."""
  result = any(value is None for value in values)
  print(f'any_are_none: {result}')
  if log_result:
    caller_frame = inspect.currentframe().f_back
    caller_locals = caller_frame.f_locals if caller_frame else {}

    for value in values:
      var_name = None
      for name, var_value in caller_locals.items():
        if var_value is None:
          var_name = name
          if var_name:
            print(f'{var_name} is None\n')
          else:
            print('Value is None\n')
  return result


def take_valid_min(
  first: float | datetime | None, second: float | datetime | None
) -> float | datetime | None:
  """Take the valid minimum of two values. Attempts to find a non-None value, but could return None if both are None."""
  return (
    min(first, second)
    if first is not None and second is not None
    else first
    if first is not None
    else second
  )


def take_valid_max(
  first: float | datetime | None, second: float | datetime | None
) -> float | datetime | None:
  """Take the valid maximum of two values. Attempts to find a non-None value, but could return None if both are None."""
  return (
    max(first, second)
    if first is not None and second is not None
    else first
    if first is not None
    else second
  )
