# coding=utf-8

import os
import logging
import string
from utils.executor import execute

_dir = os.path.abspath(os.path.dirname(__file__))
_log_filename = os.path.join(os.path.dirname(_dir), "result-run-script.log")
_result_handler_dir = os.path.join(os.path.dirname(_dir), "result_handler")
_result_log_dir = os.path.join(_result_handler_dir, "tim-results")
_result_log_dir_for_china = os.path.join(_result_handler_dir, "tim-results-china")

# for subdomains
_url_list_dir = os.path.join(os.path.dirname(_dir), 'url_list')
_subdomains_dir = os.path.join(_url_list_dir, "subdomains")


def outputAtConsole():
	logging.basicConfig(level=logging.DEBUG, format='%(message)s', filename=_log_filename, filemode="w")

	console = logging.StreamHandler()
	console.setLevel(logging.DEBUG)
	console.setFormatter(logging.Formatter("%(message)s"))
	logging.getLogger('').addHandler(console)

outputAtConsole()

# get the home directory
_home_dir = execute("echo $HOME")
# get the chrome binary
_chrome_binary = _home_dir + "/chromium/tick/src/out/Default/chrome"
logging.info(_chrome_binary)
# get the node binary
_node_binary = "node"
# get the nodejs script, which checks the loading status and gets domains for all same-origin frames
_node_filename = os.path.join(_dir, "find_subframes.js")
# timeout for each webpage
_timeout = 60

# for randomize the file name
_random_sample = string.ascii_letters + string.digits
