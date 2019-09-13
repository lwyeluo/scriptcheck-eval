import logging
import os

_logger = logging.getLogger('')

_dir = os.path.abspath(os.path.dirname(__file__))
_log_filename = os.path.join(os.path.dirname(_dir), "result-parse-log.log")

def outputAtConsole():
	_logger.setLevel(logging.DEBUG)

	# console handler
	console = logging.StreamHandler()
	console.setFormatter(logging.Formatter("%(message)s"))
	console.setLevel(logging.DEBUG)

	# log handler
	with open(_log_filename, 'w') as f:
		f.write("")
		f.close()
	log_file = logging.FileHandler(_log_filename)
	log_file.setFormatter(logging.Formatter("%(message)s"))
	log_file.setLevel(logging.DEBUG)

	_logger.addHandler(log_file)
	_logger.addHandler(console)

outputAtConsole()