import redis

r=redis.Redis()

for key in r.scan_iter("lotus:*"):
	r.delete(key)
