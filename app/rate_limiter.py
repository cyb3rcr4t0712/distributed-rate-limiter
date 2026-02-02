import redis
import json
import time
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# The Lua script for Sliding Window
# KEYS[1] = The rate limit key (e.g., rate:user123:api/resource)
# ARGV[1] = Current timestamp in milliseconds
# ARGV[2] = Window size in milliseconds
# ARGV[3] = Max allowed requests (limit)
SLIDING_WINDOW_SCRIPT = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])

-- Remove timestamps older than the window
redis.call('ZREMRANGEBYSCORE', key, '-inf', now - window)

-- Count current requests in the window
local count = redis.call('ZCARD', key)

-- Check if under limit
if count < limit then
    -- Add current timestamp
    redis.call('ZADD', key, now, now)
    -- Set expiry to clean up old keys (2 * window size for safety)
    redis.call('PEXPIRE', key, window * 2)
    return 1 -- Allowed
else
    return 0 -- Denied
end
"""

class DistributedRateLimiter:
    def __init__(self):
        self.redis = redis.from_url(REDIS_URL, decode_responses=True)
        self.script = self.redis.register_script(SLIDING_WINDOW_SCRIPT)

    def allow_request(self, client_id: str, endpoint: str, limit: int, window_ms: int) -> bool:
        """
        Checks if request is allowed.
        """
        key = f"rate:{client_id}:{endpoint}"
        now_ms = int(time.time() * 1000)
        
        # Execute atomic Lua script
        result = self.script(
            keys=[key], 
            args=[now_ms, window_ms, limit]
        )
        
        return bool(result)

    def get_current_usage(self, client_id: str, endpoint: str) -> int:
        """Helper for analytics/debugging"""
        key = f"rate:{client_id}:{endpoint}"
        return self.redis.zcard(key)

# Initialize Global Instance
limiter = DistributedRateLimiter()