import datetime


def format_timestamp(ts):
  # normalize input to a datetime
  if isinstance(ts, str):
    if ts.endswith('Z'):
      ts = ts[:-1] + '+00:00'
    dt = datetime.datetime.fromisoformat(ts)
  elif isinstance(ts, datetime.datetime):
    dt = ts
  else:
    return 'unknown'

  # ensure UTC awareness
  if dt.tzinfo is None:
    dt = dt.replace(tzinfo=datetime.timezone.utc)

  return dt.strftime('%b %d, %Y %H:%M')  # e.g. "Aug 18, 2025 14:32"
