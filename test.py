import redis

r=redis.Redis()


print(r.get('a').decode())

