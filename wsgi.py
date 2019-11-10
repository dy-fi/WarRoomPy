import eventlet
eventlet.monkey_patch(socket=True)

from app import app, io

application = app

if __name__ == "__main__":
    io.run(application, port=5000)