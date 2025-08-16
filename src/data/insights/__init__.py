import os
import yaml

DATA_DIR = os.path.dirname(__file__)

def load_insights():
  insights = []
  for filename in sorted(os.listdir(DATA_DIR)):
    if filename.endswith('.yaml'):
      path = os.path.join(DATA_DIR, filename)
      with open(path, 'r') as f:
        insight = yaml.safe_load(f)
        insights.append(insight)
  insights.sort(key=lambda x: x.get('title', '').lower())
  return insights

insights = load_insights()
