# -*- coding: utf-8 -*-
#!/usr/bin/python

from gevent import monkey; monkey.patch_all()

from gevent_zeromq import zmq
from sys import exit, argv
from os import path
from socket import gethostname

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
		except zmq.ZMQError as e:
			print "error context zmq part (%s)" % e
			exit(1)

	def send_message(self, msg=None):
		'''
		Send message to subscriber.
		'''
		try:
			json = {
				'log' : msg,
				'host' : gethostname(),
				'logfile' : self.log_file,
			}
			_doc = msg if msg else None
			self.socket.send_json(json)
		except zmq.ZMQError as e:
			print "error send zmq part (%s)" % e
			exit(2)


class Reader(ZmqPublisher):
	'''
	Reader part.
	'''
	def __init__(self, log_file, **args):
		try:
			super(Reader, self).__init__(zmq_host=host, zmq_port=port)
			print "Server start at %s:%s" % (host, port)
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
						self.send_message(line)
		except Exception, e:
			print "error launch reader part (%s)" % e
			exit(4)


if __name__ == '__main__':
	arguments = []
	try:
		if len(argv) == 1 : raise IOError 
		options, remainder = getopt.getopt(argv[1:], 'f:h:p:', ['logfile=', 'host=', 'port='])
		# -f / --file is require
		if '-f' not in str(options) and '--logfile' not in str(options) : raise IOError
		for opt, arg in options:
	 		if opt in ('-f', '--logfile'): 
	 			if not path.exists(arg) : raise Exception, "%s: No such file or directory" % arg
	 			else : _log = arg
	 		host = arg if opt in ('-h', '--host') else 'localhost'
	 		port = int(arg) if opt in ('-p', '--port') else 9999

	except IOError:
		print "Usage: reader [OPTION]... [VALUE]..."
		print "Options:"
		print "  -f, --logfile  	specify the log file to read (require)"
		print "  -h, --host 	 	hostname/ip to use for connection on zmq subscriber (default: localhost)"
		print "  -p, --port 	 	port number to use for connection on zmq subscriber (default: 6666)"
		exit(0)
	except Exception, e:
		print "error main part (%s)" % e
		exit(1)
	else:
		sub = Reader(_log, zmq_host=host, zmq_port=port)


