import os
import yaml

DATA_DIR = os.path.dirname(__file__)

def load_templates():
  templates = []
  for filename in sorted(os.listdir(DATA_DIR)):
    if filename.endswith('.yaml'):
      path = os.path.join(DATA_DIR, filename)
      with open(path, 'r') as f:
        template = yaml.safe_load(f)
        templates.append(template)
  templates.sort(key=lambda x: x.get('title', '').lower())
  return templates

templates = load_templates()
