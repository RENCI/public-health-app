import datetime


def time_ago(ts):
  # normalize input to a datetime
  if isinstance(ts, str):
    # handle UTC "Z" if needed
    if ts.endswith('Z'):
      ts = ts[:-1] + '+00:00'
    dt = datetime.datetime.fromisoformat(ts)
  elif isinstance(ts, datetime.datetime):
    dt = ts
  else:
    return 'unknown'

  # compare in UTC
  now = datetime.datetime.now(datetime.timezone.utc)
  if dt.tzinfo is None:
    dt = dt.replace(tzinfo=datetime.timezone.utc)

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
