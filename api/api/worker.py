#!/usr/bin/python
# -*- coding: utf-8 -*-

from redis import Redis
from rq import Queue, Connection, Worker

with Connection(connection=Redis(host='connectivity-redis')):
    # ssr : stop start restart kill delete ...
    w = Worker(['default', 'encrypt', 'decrypt']).work()
