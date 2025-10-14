import json
from lzstring import LZString

lz = LZString()


def generate_insight_share_url(
  round_number, insight_id: str, insights=None, base_url: str = ''
) -> str:
  if insights is None:
    insights = []

  insight = next((i for i in insights if str(i.get('id')) == str(insight_id)), None)
  if not insight:
    raise ValueError(f'Insight {insight_id} not found')

  state = {
    'round': round_number,
    'title': insight.get('title', ''),
    'description': insight.get('description', ''),
    'controls': insight.get('controls', {}),
  }

  compressed_state = lz.compressToEncodedURIComponent(json.dumps(state))
  return f'{base_url}/shared/{compressed_state}'


def extract_controls_from_share_url(pathname: str) -> dict | None:
  """Decode /shared/<compressed-state> into a state dict, or None on failure."""
  if not pathname or not pathname.startswith('/shared/'):
    return None

  encoded = pathname.removeprefix('/shared/')

  try:
    decoded = lz.decompressFromEncodedURIComponent(encoded)
    return json.loads(decoded) if decoded else None
  except Exception as error:
    print('Error decoding insight:', error)
    return None
