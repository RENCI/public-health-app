import os
import base64
import mimetypes

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

def asset_uri(relative_path: str) -> str:
  '''
  Return a data: URI for an asset inside assets/.
  Example: asset_uri('images/covid19-smh-logo.png')
  '''
  full_path = os.path.join(PROJECT_ROOT, 'assets', relative_path)
  mime_type, _ = mimetypes.guess_type(full_path)
  mime_type = mime_type or 'application/octet-stream'

  with open(full_path, 'rb') as f:
    encoded = base64.b64encode(f.read()).decode('utf-8')

  return f'data:{mime_type};base64,{encoded}'
