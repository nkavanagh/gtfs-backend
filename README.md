GTFS Backend
============

Backend code for serving up GTFS transit data. Uses [Flask](http://flask.pocoo.org).

This code is not fit for use, yet.

To-do
=====

[ ] Add optional support for a response envelope
[ ] Double check all paths, especially those dealing with user input
[x] Add value filtering capability when reading the CSV files
[ ] Version API using URL
[x] Permit filtering of service list by service_id
[x] Only include useful fields
[ ] Allow optional inclusion of the fields that aren't "useful". Expose this to consumers. First part done.
[ ] Pretty print the JSON
[ ] gzip responses
[ ] ETag based on GTFS files involved in generating a response
[ ] Last modified based on GTFS files involved in generation a response
[ ] Return 404 when a feed is not found
[ ] Return JSON data on errors. "description" for the developer, "message" for the user.
[ ] Should be able to use a trailing slash on these urls
[x] Performance: filtering trips on route_id takes half a second. GTFS trim fixed this.
[x] Performance: going to stop_times puts us at 22 seconds. ugh. Fixed by trimming the GTFS. Also ugh.
[ ] Performance: stops.txt adds 200ms to our script.
[x] Sort trips by service_id then direction
[ ] Nice to have a way of returning a dict (instead of an array) keyed on my field of choice. 1 use counted.
[ ] Put stop times inside trips in response object
[ ] Key stops on stop_id
[ ] Cache full JSON responses. Expire cache only when a source document (i.e. the GTFS) is modified.