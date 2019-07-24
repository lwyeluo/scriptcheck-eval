# coding=utf-8

import os
import logging

_dir = os.path.abspath(os.path.dirname(__file__))
_url_list_dir = os.path.join(os.path.dirname(_dir), "url_list")

_subdomains_dir = os.path.join(_url_list_dir, "subdomains")
_topsites_dir = os.path.join(_url_list_dir, "topsitesAlexa")

_log_filename = os.path.join(os.path.dirname(_dir), "result-parse-log.log")
print(_subdomains_dir, _topsites_dir)


def outputAtConsole():
	logging.basicConfig(level=logging.DEBUG, format='%(message)s', filename=_log_filename, filemode="w")

	console = logging.StreamHandler()
	console.setLevel(logging.DEBUG)
	console.setFormatter(logging.Formatter("%(message)s"))
	logging.getLogger('').addHandler(console)

outputAtConsole()

