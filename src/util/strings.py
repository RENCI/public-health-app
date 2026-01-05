from urllib.parse import parse_qs


def get_query_param(search: str, key: str, default=None):
  """Extract a single query param from Dash's url.search string."""
  if not search:
    return default
  query = parse_qs(search.lstrip('?'))
  return query.get(key, [default])[0]
