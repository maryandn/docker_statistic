import multiprocessing

bind = '0.0.0.0:8000'
worker_class = 'gthread'
workers = min(multiprocessing.cpu_count(), 4)   # 1, якщо кеш LocMem
threads = 8

timeout = 30
graceful_timeout = 20
keepalive = 5

max_requests = 2000
max_requests_jitter = 200

accesslog = None
errorlog = '-'
loglevel = 'info'