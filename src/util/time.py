from datetime import datetime, timezone


def format_timestamp(ts: str | datetime, format: str = '%b %d, %Y %H:%M') -> str:
  # normalize input to a datetime
  if isinstance(ts, str):
    if ts.endswith('Z'):
      ts = ts[:-1] + '+00:00'
    dt = datetime.fromisoformat(ts)
  elif isinstance(ts, datetime):
    dt = ts

  # ensure UTC awareness
  if dt.tzinfo is None:
    dt = dt.replace(tzinfo=timezone.utc)

  return dt.strftime(format)  # e.g. "Aug 18, 2025 14:32"


def time_ago(ts: str | datetime) -> str:
  # normalize input to a datetime
  if isinstance(ts, str):
    # handle UTC "Z" if needed
    if ts.endswith('Z'):
      ts = ts[:-1] + '+00:00'
    dt = datetime.fromisoformat(ts)
  elif isinstance(ts, datetime):
    dt = ts

  # compare in UTC
  now = datetime.now(timezone.utc)
  if dt.tzinfo is None:
    dt = dt.replace(tzinfo=timezone.utc)

  delta = now - dt
  seconds = int(delta.total_seconds())

  if seconds < 60:
    return f'{seconds} seconds ago'
  elif seconds < 3600:
    return f'{seconds // 60} minutes ago'
  elif seconds < 86400:
    return f'{seconds // 3600} hours ago'
  else:
    return f'{seconds // 86400} days ago'
