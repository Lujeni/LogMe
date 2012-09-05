# -*- coding: utf-8 -*-
#!/usr/bin/python

from gevent import monkey; monkey.patch_all()

from gevent_zeromq import zmq
from sys import exit, argv
from os import path

import time
import zmq
import gevent
import getopt


class ZmqPublisher(object):
	'''
	ZeroMQ part.
	'''
	# TODO: user decorator for debug. Print Server start ... for example
	def __init__(self, **args):
		'''
		Init zmq context:
		Should receive zmg_host & zmq_port.
		'''
		try:
			context = zmq.Context()
			self.socket = context.socket(zmq.PUB)
			self.socket.connect('tcp://%s:%d' % (args['zmq_host'], args['zmq_port']))
			print 'Message send to %s:%d' % (args['zmq_host'], args['zmq_port'])
		except zmq.ZMQError as e:
			print "error context zmq part (%s)" % e
			exit(1)

	def send_message(self, msg=None):
		'''
		Send message to subscriber.
		'''
		try:
			_doc = msg if msg else None
			self.socket.send(_doc)
		except zmq.ZMQError as e:
			print "error send zmq part (%s)" % e
			exit(2)


class Reader(ZmqPublisher):
	'''
	Reader part.
	'''
	def __init__(self, log_file, **args):
		try:
			host, port = 'localhost', 9999
			if args and args.has_key('zmq_host') and args.has_key('zmq_port') : host, port = args['zmq_host'], args['zmq_port']
			elif args and args.has_key('zmq_port') : port = args['zmq_port']
			elif args and args.has_key('zmq_host') : port = args['zmq_host']
			super(Reader, self).__init__(zmq_host=host, zmq_port=port)
			self.log_file = log_file
			self.run()
		except Exception, e:
			print "error init reader part (%s)" % e
			exit(3)

	def run(self):
		'''
		launch the reader.
		'''
		try:
			with open(self.log_file) as f:
				f.seek(0, 2)
				while True:
					where  = f.tell()
					line = f.readline()
					if not line:
						time.sleep(0.1)
						f.seek(where)
					else: 
						self.socket.send(line)
		except Exception, e:
			print "error launch reader part (%s)" % e
			exit(4)


if __name__ == '__main__':
	try:
		if len(argv) == 1 : raise IOError 
		options, remainder = getopt.getopt(argv[1:], 'f:', ['logfile='])
		for opt, arg in options:
	 		if opt in ('-f', '--logfile') : 
	 			if not path.exists(arg) : raise Exception, "%s: No such file or directory" % arg
	 			else : _log = arg
	except IOError:
		print "Usage: ls [OPTION]... [FILE]..."
		print "List information about the FILEs (the current directory by default).\n"
		print "Options:"
		print "  -f, --logfile  	specify the log file to read"
		exit(1)
	except Exception, e:
		print "error main part (%s)" % e
		exit(1)
	else:
		sub = gevent.spawn(Reader(_log, zmq_host='localhost', zmq_port=6666))