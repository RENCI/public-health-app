import pickle
from typing import Any

import redis


class RedisChartCache:
  def __init__(self, host='localhost', port=6379, db=0):
    self.redis_client = redis.Redis(host=host, port=port, db=db)
    self.expire_time = 3600  # 1 hour

  def get(self, key: str):
    cached_data = self.redis_client.get(key)
    if cached_data:
      return pickle.loads(cached_data)
    return None

  def set(self, key: str, value: Any):
    serialized = pickle.dumps(value)
    self.redis_client.setex(key, self.expire_time, serialized)
