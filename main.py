#!/usr/bin/python

from flask import Flask, jsonify, abort, make_response, request
from flask_sqlalchemy import SQLAlchemy
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import urlparse

app = Flask(__name__)


# Set up postgres db connection
urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

conn = psycopg2.connect(
	database=url.path[1:],
	user=url.username,
	password=url.password,
	host=url.hostname,
	port=url.port
)

# GET / POST for leaderboard entries
@app.route('/api/leaderboard/<int:l_num>/entries', methods=['GET', 'POST'])
def get_entry(l_num):
	# cursor object used to perform postgres db queries
	cur = conn.cursor(cursor_factory=RealDictCursor)

	if request.method == 'GET':
		if request.args.has_key('user'):
			user_name = request.args.get('user')
			cur.execute("SELECT net_id, time FROM leaderboard WHERE net_id = '{}' AND ass_num = {};".format(user_name, l_num))
			return json.dumps(cur.fetchall(), indent=2)
		else:
			cur.execute("SELECT net_id, time FROM leaderboard WHERE ass_num = '{}';".format(l_num))
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
		cur.execute("INSERT INTO leaderboard (net_id, time, ass_num) VALUES ('{}', {}, {});".format(net_id, time, l_num))
		conn.commit()
		return make_response(jsonify({'success': 'entry added'}), 404)
	return 'something went wrong...'

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, use_reloader=False, debug=True)