import redis
import json
from flask import current_app

def get_redis_connection():
    """Get Redis connection"""
    try:
        redis_url = current_app.config['REDIS_URL']
        return redis.from_url(redis_url)
    except Exception as e:
        print(f"Redis connection error: {e}")
        return None

def push_event_to_queue(event_id):
    """Push event to Redis queue for claim processing"""
    try:
        r = get_redis_connection()
        if r:
            queue_data = {
                'event_id': event_id,
                'timestamp': str(json.dumps(str(event_id)))
            }
            r.lpush('event_queue', json.dumps(queue_data))
            return True
        return False
    except Exception as e:
        print(f"Queue push error: {e}")
        return False

def pop_event_from_queue():
    """Pop event from Redis queue"""
    try:
        r = get_redis_connection()
        if r:
            data = r.rpop('event_queue')
            if data:
                return json.loads(data)
        return None
    except Exception as e:
        print(f"Queue pop error: {e}")
        return None
