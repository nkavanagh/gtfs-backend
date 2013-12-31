import os
import csv
from operator import itemgetter
from flask import Flask, url_for, Response, json

# consts; must be a better place for these

GTFS_ROUTE_TYPE_TRAM = '0'
GTFS_ROUTE_TYPE_SUBWAY = '1'
GTFS_ROUTE_TYPE_RAIL = '2'
GTFS_ROUTE_TYPE_BUS = '3'
GTFS_ROUTE_TYPE_FERRY = '4'
GTFS_ROUTE_TYPE_CABLECAR = '5'
GTFS_ROUTE_TYPE_GONDOLA = '6'
GTFS_ROUTE_TYPE_FUNICULAR = '7'

# the app

app = Flask(__name__)

# TODO: move configuration out of here
app.config.update(
    DEBUG=True,
    GTFS_DIR='/Users/niall/GTFS'
)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

# utility functions

# read a csv file and return each row as a dictionary keyed off the 
# columns that are presumably in the first line of the csv
# filename is first positional arg, dictionary used for filtering
def read_csv(*args, **kwargs):
	print args
	print kwargs
	csv_filename = args[0]
	f  = open(csv_filename, "rb")
	reader = csv.reader(f)
	rows = []
	linenum = 0
	
	for line in reader:
		# Save header row.
		if linenum == 0:
			header = line
		else:
			row = {}
			colnum = 0
			for col in line:
				# all fields, or just some?
				if 'fields' in kwargs:
					# just some
					if header[colnum] in kwargs['fields']:
						row[header[colnum]] = col
				else:
					# all fields
					row[header[colnum]] = col
					
				colnum += 1
				
			# are we filtering?
			if 'filter' in kwargs:
				for k in kwargs['filter'].keys():
					if k in row:
						if isinstance(kwargs['filter'][k], list):
							# for array values, test that it is 'in'
							if row[k] in kwargs['filter'][k]:
								rows.append(row)
						elif row[k] == kwargs['filter'][k]:
							# for scalar values, test equality
							rows.append(row)
			else:
				# no filtering, just add it
				rows.append(row)
	
		linenum += 1
	
	f.close()
	return rows

# construct a HTTP JSON response for some data
def create_response(data):
	js = json.dumps(data)

	response = Response(js, status=200, mimetype='application/json')

	return response
	
# routing

@app.route('/')
def feeds():
	feeds = []
	for filename in os.listdir(app.config['GTFS_DIR']):
		feed = { 'feed_name': filename }
		feed['agencies'] = read_csv(app.config['GTFS_DIR'] + '/' + filename + '/agency.txt')
		feeds.append(feed)
	
	return create_response(feeds)

@app.route('/<feedname>')
def routes(feedname):
	filename = app.config['GTFS_DIR'] + '/' + feedname + '/routes.txt'
	routes = read_csv(filename, fields=[ 'route_id', 'route_long_name', 'route_type' ])
	
	return create_response(routes)
	
@app.route('/<feedname>/rail')
def rail_routes(feedname):
	filename = app.config['GTFS_DIR'] + '/' + feedname + '/routes.txt'
	routes = read_csv(filename, 
					filter={ 'route_type': GTFS_ROUTE_TYPE_RAIL },
					fields=[ 'route_id', 'route_long_name', 'route_type' ] )

	return create_response(routes)
	
@app.route('/<feedname>/<route_id>')
def route(feedname, route_id):
	filename = app.config['GTFS_DIR'] + '/' + feedname + '/trips.txt'
	trips = read_csv(filename, 
					filter={ 'route_id': route_id },
					fields=[ 'direction_id', 'route_id', 'service_id', 'trip_headsign', 'trip_id' ])
					
	trips = sorted(trips, key=itemgetter('service_id', 'direction_id'))
	
	trip_ids = []
	
	for trip in trips:
		trip_ids.append(trip['trip_id'])
		
	# grab stop times and stops for these trips
	filename = app.config['GTFS_DIR'] + '/' + feedname + '/stop_times.txt'
	stop_times = read_csv(filename, 
						filter={ 'trip_id': trip_ids },
						fields=[ 'departure_time', 'drop_off_type', 'pickup_type', 'stop_id', 'stop_sequence', 'trip_id' ])
						
	stop_times = sorted(stop_times, key=itemgetter('trip_id', 'stop_sequence'))

	stop_ids = []
	
	for stop_time in stop_times:
		stop_ids.append(stop_time['stop_id'])
	
	filename = app.config['GTFS_DIR'] + '/' + feedname + '/stops.txt'
	stops = read_csv(filename, 
	  				filter={ 'stop_id': stop_ids },
					fields=[ 'stop_id', 'stop_lon', 'stop_lat', 'stop_name' ])
	
	route = { 'trips': trips, 'stop_times': stop_times, 'stops': stops }
	
	return create_response(route)
	
if __name__ == '__main__':
	app.run()
