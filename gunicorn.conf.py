# gunicorn.conf.py — G1 DE IDEIAS produção
import multiprocessing

bind = "0.0.0.0:5000"
workers = 2  # suficiente pro moto g84 / Mint
threads = 4
worker_class = "gthread"
timeout = 30
keepalive = 2
accesslog = "-"
errorlog = "-"
loglevel = "info"
preload_app = True
forwarded_allow_ips = "*"
