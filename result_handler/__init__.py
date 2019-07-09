# coding=utf-8

import os
import logging

_dir = os.path.abspath(os.path.dirname(__file__))
_top_site_dir = os.path.join(os.path.dirname(_dir), "top_sites")
_log_filename = os.path.join(os.path.dirname(_dir), "result-parse-log.log")
_result_dir = os.path.join(_dir, "tim-results")
print(_top_site_dir)


def outputAtConsole():
	logging.basicConfig(level=logging.DEBUG, format='%(message)s', filename=_log_filename, filemode="w")

	console = logging.StreamHandler()
	console.setLevel(logging.DEBUG)
	console.setFormatter(logging.Formatter("%(message)s"))
	logging.getLogger('').addHandler(console)

outputAtConsole()

