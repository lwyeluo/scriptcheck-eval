# coding=utf-8

import os
import logging

_dir = os.path.abspath(os.path.dirname(__file__))
_url_list_dir = os.path.join(os.path.dirname(_dir), "url_list")

_subdomains_dir = os.path.join(_url_list_dir, "subdomains")
_topsites_dir = os.path.join(_url_list_dir, "topsitesAlexa")
_topsites_china_dir = os.path.join(_url_list_dir, "topsitesChina")

_topsites_output_domain_dir = os.path.join(_topsites_dir, "suspectedSubDomains")

_log_filename = os.path.join(os.path.dirname(_dir), "result-parse-log.log")
print(_subdomains_dir, _topsites_dir)

_logger = logging.getLogger("myLogger")

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

	_logger.addHandler(console)
	_logger.addHandler(log_file)

outputAtConsole()

