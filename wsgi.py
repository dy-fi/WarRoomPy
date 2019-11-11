from gevent import monkey
monkey.patch_all()

import os
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

from app import app, io

application = app

if __name__ == "__main__":
    io.run(application, port=5000)