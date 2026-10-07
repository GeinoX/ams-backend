import redis

r = redis.Redis(host="127.0.0.1", port=6379, db=0)

print(r.ping())
print(r.lpush("debug_test", "hello"))
print(r.lpop("debug_test"))