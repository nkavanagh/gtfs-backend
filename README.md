GTFS Backend
============

Backend code for serving up GTFS transit data. Uses [Flask](http://flask.pocoo.org).

This code is probably not fit for use just yet.

GTFS data
---------

Put it in a directory called `instance/feeds`; e.g.
`instance/feeds/mbta/stops.txt`, etc. You can serve up multiple feeds.

Running locally
---------------

```zsh
$ virtualenv venv   # first time
$ source venv/bin/activate
$ pip install -r requirements.txt
$ ./application.py
```

Running on AWS
--------------

```zsh
$ eb init
$ eb start
$ git aws.push      # when you make changes
$ eb stop           # when you're done
$ eb delete         # if you want to clean it all up
```

The first time the environment is created in AWS, it will attempt to download
GTFS data for the MBTA. You can modify this behavior by editing
`scripts/prepareenv.sh`.
