import os
import csv
from operator import itemgetter
from flask import Flask, url_for, Response, json, render_template, abort

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
app.config.from_envvar('GTFS_BACKEND_SETTINGS')

# utility functions

# read a csv file and return each row as a dictionary keyed off the 
# columns that are presumably in the first line of the csv
# filename is first positional arg
# named arg fields controls what fields are returned
# named arg filters specifies some comparison check on rows 
# named arg keyed_on returns a dictionary keyed on the specified column
def read_csv(*args, **kwargs):
	csv_filename = args[0]
	f  = open(csv_filename, "rb")
	reader = csv.reader(f)
	rows = []
	
	if 'keyed_on' in kwargs:
		rows = {}
		
	linenum = 0
	
	for line in reader:
		# Save header row.
		if linenum == 0:
			header = line
		else:
			row = {}
			colnum = 0
			for col in line:
				# is this numeric?
				
				try:
					numval = int(col)
					col = numval
				except ValueError:
					# really?
					try:
						numval = float(col)
						col = numval
					except ValueError:
						pass
					pass # no-op
					
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
								if 'keyed_on' in kwargs:
									rows[row[kwargs['keyed_on']]] = row
								else:
									rows.append(row)
						elif row[k] == kwargs['filter'][k]:
							# for scalar values, test equality
							if 'keyed_on' in kwargs:
								rows[row[kwargs['keyed_on']]] = row
							else:
								rows.append(row)
			else:
				# no filtering, just add it
				if 'keyed_on' in kwargs:
					rows[row[kwargs['keyed_on']]] = row
				else:
					rows.append(row)
	
		linenum += 1
	
	f.close()
	return rows

# construct a HTTP JSON response for some data
def create_response(data):
	print 'Creating a response for %s' % (data)
	response = json.jsonify(data)
	return response
	
# build a dictionary from a sequence
def build_dictionary(seq, key):
    return dict((d[key], dict(d)) for d in seq)

# filter sequence of dictionaries. will match anything. not ideal. TODO.
def filter_dictionaries(*args, **kwargs):
	filtered = []
	
	for item in args[0]:
		for key in kwargs.keys():
			print "Checking for %s in %s" % (key, item)
			if key in item:
				if item[key] == kwargs[key]:
					filtered.append(item)
			
	return filtered
		

# routing

@app.route('/')
def feeds():
	feeds = []
	print 'Checking in %s for feeds' % ( app.config['GTFS_DIR'] )
	for filename in os.listdir(app.config['GTFS_DIR']):
		if filename not in app.config['GTFS_FEEDS']:
			continue
			
		feed = { 'feed_name': filename }
		feed['agencies'] = read_csv(app.config['GTFS_DIR'] + '/' + filename + '/agency.txt')
		feeds.append(feed)
	
	return create_response(feeds)

@app.route('/<feedname>/')
def routes(feedname):
	if feedname not in app.config['GTFS_FEEDS']:
		abort(404)
		
	filename = app.config['GTFS_DIR'] + '/' + feedname + '/routes.txt'
	routes = read_csv(filename, fields=[ 'route_id', 'route_long_name', 'route_type' ])
	
	return create_response(routes)
	
@app.route('/<feedname>/rail/')
def rail_routes(feedname):
	filename = app.config['GTFS_DIR'] + '/' + feedname + '/routes.txt'
	routes = read_csv(filename, 
					filter={ 'route_type': GTFS_ROUTE_TYPE_RAIL },
					fields=[ 'route_id', 'route_long_name', 'route_type' ] )

	return create_response(routes)
	
@app.route('/<feedname>/<route_id>/')
@app.route('/<feedname>/rail/<route_id>/')
def route(feedname, route_id):
	filename = app.config['GTFS_DIR'] + '/' + feedname + '/trips.txt'
	trips = read_csv(filename, 
					filter={ 'route_id': route_id },
					fields=[ 'direction_id', 'route_id', 'service_id', 'trip_headsign', 'trip_id' ],
					keyed_on='trip_id')
					
	#trips = sorted(trips, key=itemgetter('service_id', 'direction_id'))
	
	trip_ids = trips.keys()
	
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
					fields=[ 'stop_id', 'stop_lon', 'stop_lat', 'stop_name' ],
					keyed_on='stop_id')
	
	# get the service information for these trips
	service_ids = list(set([trip['service_id'] for trip in trips.values()]))
	filename = app.config['GTFS_DIR'] + '/' + feedname + '/calendar.txt'
	services = read_csv(filename, 
						filter={ 'service_id': service_ids },
						keyed_on='service_id'
						)
						
	# TODO: deal with calendar_dates
	
	# Each service should contain its trips
	for service_id in service_ids:
		service_trips = filter_dictionaries(trips.values(), service_id=service_id)
		services[service_id]['trips'] = build_dictionary(service_trips, 'trip_id')
		
		# each trip contains its stops
		for trip_id in services[service_id]['trips'].keys():
			services[service_id]['trips'][trip_id]['stops'] = filter_dictionaries(stop_times, trip_id=trip_id)
	
	# generate response
	route = { 'services': services, 'stops': stops }
	
	return create_response(route)
	
if __name__ == '__main__':
	app.run()
