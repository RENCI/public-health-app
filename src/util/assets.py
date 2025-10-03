import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))


def asset_uri(relative_path: str) -> str:
  """
  build a URI for an asset inside the project root assets/ dir,
  e.g., asset_uri('images/covid19-smh-logo.png')
  """
  full_path = os.path.join(PROJECT_ROOT, 'assets', relative_path)
  return f'file://{full_path}'
