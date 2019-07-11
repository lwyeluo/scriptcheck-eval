# coding=utf-8

import os
import logging
from utils.executor import execute

_dir = os.path.abspath(os.path.dirname(__file__))
_log_filename = os.path.join(os.path.dirname(_dir), "result-run-script.log")
_result_handler_dir = os.path.join(os.path.dirname(_dir), "result_handler")
_result_log_dir = os.path.join(_result_handler_dir, "tim-results")


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
# get the nodejs script
_node_filename = os.path.join(_dir, "checkUrlLoadCompleted.js")
# timeout for each webpage
_timeout = 60