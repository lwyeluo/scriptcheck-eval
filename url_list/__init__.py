# coding=utf-8

import os

_dir = os.path.abspath(os.path.dirname(__file__))
_subdomains_dir = os.path.join(_dir, "subdomains")

if not os.path.exists(_subdomains_dir):
	from utils.executor import execute
	execute("mkdir -p %s" % _subdomains_dir)
