# [War Room](war-room-py.herokuapp.com) 💻 📡 

Pull data from anywhere on the web and make live graphs without being a programmer.  This is a proof of concept that happened to work out!

-----

# How to use

You'll be prompted for a `URL` and `Xpath` to make a "place".  These places point to one piece of data we can collect to make a time-series graph.  

A collection of places makes up the dashboards we call "Rooms", presenting them however you want, like this-

!["coinbase-example"](/static/coinbase-example.png)


# Road Map

* Live graphs

* Better frontend

* User Authentication

-----

## Running Locally

Make sure you have [Python 3](https://docs.python.org/3/) and [MongoDB](https://www.mongodb.com/) installed.

```sh
git clone https://github.com/dy-fi/war-room-py.git
cd war-room-py
pip3 install -r requirements.txt
python3 app.py
```

The app should now be running on [localhost:5000](http://localhost:5000/). Make sure MongoDB is installed and MongoDB Daemon is running.

## Running Locally With Docker

Coming soon!

---

## Built With
* [Flask](https://flask.palletsprojects.com/en/1.1.x/) - Web framework
* [Flask SocketIO/SocketIO](https://socket.io/) - Socket Connection
* [MongoDb](https://www.mongodb.com/) - Document Based Database
* [Gunicorn](https://gunicorn.org/) - Web Server

## Deployed With

[Docker](https://www.docker.com/) - Containerization and Cluster Fabrication (coming soon)


Staging - [Heroku](heroku.com) - VPS cloud hosting

Production - Coming Soon

---

### Author
Dylan Finn | [Github](https://github.com/dy-fi/) | [LinkedIn](https://www.linkedin.com/in/dylan-finn-a36b9614b/) | [Portfolio](https://www.makeschool.com/portfolio/Dylan-Finn)