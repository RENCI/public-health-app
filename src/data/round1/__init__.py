import os
import yaml

DATA_DIR = os.path.join(os.path.dirname(__file__), 'insights')

def load_insights():
  insights = []
  for filename in sorted(os.listdir(DATA_DIR)):
    if filename.endswith('.yaml'):
      path = os.path.join(DATA_DIR, filename)
      with open(path, 'r') as f:
        insight = yaml.safe_load(f)
        insight['type'] = 'system'
        insights.append(insight)
  insights.sort(key=lambda x: x.get('title', '').lower())
  return insights

insights = load_insights()

def get_insight(insight_id: str | None, custom_insights=None):
  """Return a single insight by ID, or None if not found."""
  if not insight_id:
      return None
  all_insights = insights + (custom_insights or [])
  return next((x for x in all_insights if x.get('id') == insight_id), None)