from urllib.parse import parse_qs


def to_natural_list(items: list[str]) -> str:
    """
    Converts a list of strings into a grammatically correct, human-readable string.
    e.g. ['a', 'b', 'c'] -> 'a, b, and c'
    """
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f'{", ".join(items[:-1])}, and {items[-1]}'



def get_query_param(search: str, key: str, default=None):
  """Extract a single query param from Dash's url.search string."""
  if not search:
    return default
  query = parse_qs(search.lstrip('?'))
  return query.get(key, [default])[0]
