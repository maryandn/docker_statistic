import multiprocessing

bind = '0.0.0.0:8000'
worker_class = 'gthread'
workers = min(multiprocessing.cpu_count(), 4)
threads = 8

timeout = 30
graceful_timeout = 20
keepalive = 5

max_requests = 20000
max_requests_jitter = 2000

accesslog = None
errorlog = '-'
loglevel = 'info'