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
