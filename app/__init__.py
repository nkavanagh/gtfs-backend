import os
import csv
from flask import Flask, url_for, Response, json

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
def read_csv(csv_filename):
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
				row[header[colnum]] = col
				colnum += 1
				
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
@app.route('/agencies')
def agencies():
	agencies = []
	for filename in os.listdir(app.config['GTFS_DIR']):
		rows = read_csv(app.config['GTFS_DIR'] + '/' + filename + '/agency.txt')
		agencies.append(rows)
	
	return create_response(agencies)

@app.route('/agencies/<agencyid>')
def agency(agencyid):
	return 'List of services for ' + url_for('agency', agencyid=agencyid)

@app.route('/agencies/<agencyid>/<serviceid>')
def api_article(agencyid, serviceid):
	return agencyid + ' runs the ' + serviceid + ' service'

if __name__ == '__main__':
	app.run()
	