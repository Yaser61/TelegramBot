import redis
import os
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()

class RedisConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.client = redis.StrictRedis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=int(os.getenv("REDIS_DB", 0)),
                decode_responses=True
            )
        return cls._instance

    def get_client(self):
        return self.client
