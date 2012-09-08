#!/usr/bin/env python
from gevent import monkey; monkey.patch_all()

import argparse
import gevent
import json

from socketio import socketio_manage
from socketio.server import SocketIOServer
from socketio.namespace import BaseNamespace

from gevent_zeromq import zmq
import bottle as b


sessions = set()

class LogStreamNS(BaseNamespace):
	def on_get_logs(self):
		""" A new client wants to be fed """
		sessions.add(self)
		print "active sessions : %s" % len(sessions)

	def recv_disconnect(self):
		""" Bye bye, remove the session from our set """
		try:
			sessions.remove(self)
		except:
			pass
		finally:
			print "active sessions : %s" % len(sessions)
			self.disconnect(silent=True)

class SubLogger():
	def __init__(self):
		context = zmq.Context()
		self.socket = context.socket(zmq.SUB)
		self.socket.setsockopt(zmq.SUBSCRIBE, '')
		self.socket.bind("tcp://*:6666")
		self.run()

	def emit(self, name, value):
		for handler in sessions:
			handler.emit(name, json.dumps(value))

	def run(self):
		while True:
			msg = self.socket.recv_json()
			print msg
			self.emit('logs',
				{
					'host': msg['host'],
					'logfile': msg['logfile'],
					'text': msg['log'],
				}
			)

def http404(start_response):
	""" 404 handler """
	start_response('404 Not Found', [])
	return []

def application(env, start_response):
	""" Our web serving app """
	path = env['PATH_INFO'].strip('/') or 'index.html'

	# static stuff
	if path.startswith('static/') or path == "index.html":
		try:
			data = open(path).read()
		except Exception:
			return http404(start_response)

		if path.endswith(".js"):
			content_type = "text/javascript"
		elif path.endswith(".css"):
			content_type = "text/css"
		elif path.endswith(".png"):
			content_type = "image/png"
		elif path.endswith(".swf"):
			content_type = "application/x-shockwave-flash"
		else:
			content_type = "text/html"

		start_response('200 OK', [('Content-Type', content_type)])
		return [data]

	# socketIO request
	if path.startswith('socket.io/'):
		socketio_manage(env, {'': LogStreamNS})
	else:
		return http404(start_response)

if __name__ == '__main__':
	""" Main command line run """
	try:
		server = SocketIOServer(
			('0.0.0.0', 8000), application, resource='socket.io', policy_server=True, policy_listener=('0.0.0.0', 10843)
		)

		sub = gevent.spawn(SubLogger)
		sub.link(server.stop)

		server.serve_forever()
	except KeyboardInterrupt:
		server.stop()
