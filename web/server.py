#!/usr/bin/env python
# encoding: utf-8
"""
server.py

Created by Jorge Velázquez on 2010-04-24.
"""

import cgi
import datetime
import sqlite3
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

damage_fields = ['SPELL_DAMAGE', 'SPELL_PERIODIC_DAMAGE', 'SWING_DAMAGE', 'RANGE_DAMAGE']
healing_fields = ['SPELL_HEAL', 'SPELL_PERIODIC_HEAL']
other_fields = ['SPELL_MISSED']
tracked_fields = damage_fields + healing_fields + other_fields

class Effect:
	def __init__(self, name):
		self.name = name
		self.healing = 0
		self.damage = 0
		self.hits = 0
		self.ticks = 0
		self.resists = 0
		self.misses = 0
		self.crits = 0
		self.periodic_crits = 0
		self.blocked = 0
		self.parried = 0
		self.absorbed = 0

class Destination:
	def __init__(self, id, name):
		self.id = id
		self.name = name
		self.damage = 0
		self.healing = 0
		self.start_time = None
		self.end_time = None
		self.effects = {}

class Source:
	def __init__(self, id, name):
		self.id = id
		self.name = name
		self.damage = 0
		self.healing = 0
		self.destinations = {}

class MyHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path.endswith('.css') or self.path.endswith('.js') or self.path.endswith('.jpg'):
			f = open(curdir + sep + self.path)
			self.wfile.write(f.read())
			f.close()
		else:
			# some kind of html page
			self.wfile.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">')
			self.wfile.write('<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n')
			self.wfile.write('<head>\n')
			self.wfile.write('<title>World of Warcraft Combat Log Parser</title>\n')
			if self.path == '/':
				self.wfile.write('<link rel="stylesheet" href="/stylesheets/styles.css" type="text/css" />\n')
				self.wfile.write('<link rel="stylesheet" href="/stylesheets/awesome-buttons.css" type="text/css" />\n')
				self.wfile.write('</head>\n')
				self.wfile.write('<body>\n')
				self.wfile.write('<h1>World of Warcraft Combat Log Parser</h1>\n')
				self.wfile.write('<div><a class="awesome gray" href="/upload">Upload Combat Log</a></div>\n')
			elif self.path == '/upload':
				self.wfile.write('<link rel="stylesheet" href="/stylesheets/styles.css" type="text/css" />\n')
				self.wfile.write('<link rel="stylesheet" href="/stylesheets/awesome-buttons.css" type="text/css" />\n')
				self.wfile.write('<script type="text/javascript" src="/js/jquery.min.js"></script>\n')
				self.wfile.write('<script type="text/javascript" src="/js/upload.js"></script>\n')
				self.wfile.write('</head>\n')
				self.wfile.write('<body>\n')
				self.wfile.write('<h1>Upload Combat Log</h1>\n')
				self.wfile.write('<form method="post" enctype="multipart/form-data" action="/upload">\n')
				self.wfile.write('<p><label for="name">Raid Name:</label> <input type="text" id="name" name="name" size="40" maxlength="80" /></p>\n')
				self.wfile.write('<p><input type="file" id="file" name="file" /></p>\n')
				self.wfile.write('<p><input class="awesome gray" type="submit" id="submit" value="Upload" /></p>\n')
				self.wfile.write('</form>\n')
			elif self.path == '/raids':
				self.wfile.write('<link rel="stylesheet" href="/stylesheets/styles.css" type="text/css" />\n')
				self.wfile.write('<link rel="stylesheet" href="/stylesheets/awesome-buttons.css" type="text/css" />\n')
				self.wfile.write('</head>\n')
				self.wfile.write('<body>\n')
				self.wfile.write('<h1>Raid Listing</h1>\n')
				self.wfile.write('<p><a class="awesome gray" href="/upload">Upload Combat Log</a></p>\n')
				self.wfile.write('<table>\n')
				conn = sqlite3.connect('/tmp/wowparse.db')
				cursor = conn.cursor()
				cursor.execute('select * from raid order by created desc')
				for row in cursor:
					self.wfile.write('<tr><td><a href="/raids?id=%d">%s</a></td></tr>\n' % (row[0], row[1]))
				cursor.close()
				conn.close()
				self.wfile.write('</table>\n')
			self.wfile.write('</body>\n')
			self.wfile.write('</html>\n')
		
	def do_POST(self):
		if self.path == '/upload':
			# get our form data
			content_type, pdict = cgi.parse_header(self.headers.getheader('Content-Type'))
			query = cgi.parse_multipart(self.rfile, pdict)
			data = query.get('file')[0]
			raid_name = query.get('name')[0]
			
			# parse the combat log here
			html = self.parse_data(data)
			
			# save the html to the database
			conn = sqlite3.connect('/tmp/wowparse.db')
			cursor = conn.cursor()
			cursor.execute("insert into raid(name, html, created) values(?, ?, datetime('now'))", [raid_name, html])
			conn.commit()
			cursor.close()
			conn.close()
			
			# redirect the user to the raid listing page
			self.send_response(301)
			self.send_header('Location', '/raids')
			self.end_headers()
			
	def parse_data(self, data):
		# hashes for calculating stats
		sources = {}
		
		# start our read loop
		lines = data.split('\r\n')
		for line in lines:
			# two spaces are used to split the date/time field from the actual combat data
			major_fields = line.split('  ')
			if len(major_fields) < 2:
				continue

			# save off the date/time info, we convert later but only if we need to (i.e., we have a log entry that we are interested in)
			date_time = major_fields[0]

			# here we provide our own line parser, since we have fields which may contain separators and are wrapped in quotes
			combat_fields = major_fields[1].split(',')

			# must be one of the events that we actually track
			if not combat_fields[0] in tracked_fields:
				continue

			# if source or destination id is zero, we can't do anything with it
			srcguid = int(combat_fields[1], 16)
			dstguid = int(combat_fields[4], 16)
			if srcguid == 0 or dstguid == 0:
				continue

			# strip surrounding double-quots from source and destination names
			srcname = combat_fields[2][1:-1]
			dstname = combat_fields[5][1:-1]
			effect_type = combat_fields[0]
	
			# get the timestamp (NOTE: year is not supplied in the combat log, this will cause problems if log file crosses a year boundary)
			timestamp = datetime.datetime.strptime(date_time, '%m/%d %H:%M:%S.%f')

			# depending on how many fields we have, damage/healing amount could be in two places
			num_fields = len(combat_fields)
			if num_fields == 16:
				amount = int(combat_fields[7])
			elif num_fields == 19:
				amount = int(combat_fields[10])
			else:
				amount = 0 # other type of field
		
			# add or get source
			if srcguid in sources:
				source = sources[srcguid]
			else:
				source = Source(srcguid, srcname)
				sources[srcguid] = source

			# add or get destination
			if dstguid in source.destinations:
				destination = source.destinations[dstguid]
			else:
				destination = Destination(dstguid, dstname)
				source.destinations[dstguid] = destination
	
			# update the stats for the destination
			if effect_type in damage_fields:
				destination.damage += amount
			elif effect_type in healing_fields:
				destination.healing += amount

			# destination gets the timestamps, for dps/hps calculation
			if not destination.start_time:
				destination.start_time = timestamp
			destination.end_time = timestamp

			# add or get effect
			if effect_type == 'SWING_DAMAGE':
				effect_name = "Swing"
			else:
				effect_name = combat_fields[8][1:-1]
			if effect_name in destination.effects:
				effect = destination.effects[effect_name]
			else:
				effect = Effect(effect_name)
				destination.effects[effect_name] = effect
	
			# update effect stats
			if effect_type == 'SPELL_MISSED':
				effect.misses += 1
			elif effect_type in damage_fields:
				effect.damage += amount
				if effect_type == 'SPELL_PERIODIC_DAMAGE':
					effect.ticks += 1
				else:
					effect.hits += 1
			elif effect_type in healing_fields:
				effect.healing += amount
				if effect_type == 'SPELL_PERIODIC_HEAL':
					effect.ticks += 1
				else:
					effect.hits += 1
					
		# we're done parsing, generate some html and save it to the database
		html = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
		html += '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n'
		html += '</html>\n'
		return html
		
def main():
	try:
		server = HTTPServer(('', 8000), MyHandler)
		print 'starting http server...'
		server.serve_forever()
	except KeyboardInterrupt:
		print '^C received, shutting down server...'
		server.socket.close()

if __name__ == '__main__':
	main()
