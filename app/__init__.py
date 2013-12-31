from flask import Flask, url_for
app = Flask(__name__)

@app.route('/')
@app.route('/agencies')
def agencies():
	return 'List of agencies'

@app.route('/agencies/<agencyid>')
def agency(agencyid):
	return 'List of services for ' + url_for('agency', agencyid=agencyid)

@app.route('/agencies/<agencyid>/<serviceid>')
def api_article(agencyid, serviceid):
	return agencyid + ' runs the ' + serviceid + ' service'

if __name__ == '__main__':
	app.run()
	