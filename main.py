#!/usr/bin/python

from flask import Flask, jsonify, abort, make_response, request
from flask_sqlalchemy import SQLAlchemy
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import urlparse

app = Flask(__name__)

urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

conn = psycopg2.connect(
	database=url.path[1:],
	user=url.username,
	password=url.password,
	host=url.hostname,
	port=url.port
)

entries = [
	{
		'name': u'jtw37',
		'score': 153,
	},
	{
		'name': u'djd66',
		'score': 123,
	},
	{
		'name': u'aec69',
		'score': 152,
	}
]

@app.route('/api/leaderboard/entries', methods=['GET', 'POST'])
def get_entry():
	# cursor object used to perform postgres db queries
	cur = conn.cursor(cursor_factory=RealDictCursor)

	if request.method == 'GET':
		if request.args.has_key('user'):
			user_name = request.args.get('user')
			entry_matches = [entry for entry in entries if entry['name'] == user_name]
			if len(entry_matches) == 0:
				abort(404)
			return jsonify({'entries': entry_matches[0]})
		else:
			cur.execute("SELECT net_id, time FROM locations")
			return json.dumps(cur.fetchall(), indent=2)
	else:
		content = request.get_json()
		if content == None:
			return make_response(jsonify({'error': 'content body empty'}), 404) 
		net_id = content['net_id']
		time = content['time']
		if net_id == None or time == None:
			return make_response(jsonify({'error': 'net_id or time not provided'}), 404) 
		print "NET ID: {} : {}".format(net_id, str(time))
		cur.execute("INSERT INTO leaderboard (net_id, time) VALUES ('{}', {});".format(net_id, time))
		conn.commit()
		return make_response(jsonify({'success': 'entry added'}), 404)
	return 'something went wrong...'

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, use_reloader=False, debug=True)