# coding=utf-8

import logging
import signal
import os
from threading import Timer
from utils.executor import *

from run_script import _chrome_binary, _node_binary, _node_filename, _timeout


class RunUrl(object):
	def __init__(self, url, ret_filename):
		self.url = url
		self.ret_filename = ret_filename

		self.run()

	def timeoutCallback(self, process_node):
		logging.info("\t\tEnter timeoutCallback")
		try:
			os.killpg(process_node.pid, signal.SIGKILL)
		except Exception as error:
			logging.info(error)

	def run(self):
		ret_fd = open(self.ret_filename, 'w')

		print(_chrome_binary)
		process_chrome = subprocess.Popen([_chrome_binary, '--remote-debugging-port=9222'], stderr=ret_fd,
										  stdout=ret_fd)
		logging.info('>>> START ' + self.url)

		time.sleep(10)

		print(_node_binary, _node_filename)
		process_node = subprocess.Popen([_node_binary, _node_filename, self.url], stdout=subprocess.PIPE,
										stderr=subprocess.PIPE, preexec_fn=os.setsid)
		# create a timer
		my_timer = Timer(_timeout, self.timeoutCallback, [process_node])
		my_timer.start()

		stdout, _ = process_node.communicate()
		if '''result: { type: 'string', value: 'complete' }''' in str(stdout):
			logging.info("\t\tweb page [%s] is completed!" % self.url)
		else:
			logging.info(stdout)
			logging.info("\t\tweb page [%s] is TIMEOUT!" % self.url)
		logging.info('>>> FINISH ' + self.url)

		my_timer.cancel()

		time.sleep(5)
		# kill chrome
		try:
			logging.info("\t>>> kill Chrome [%d]" % process_chrome.pid)
			os.kill(process_chrome.pid, signal.SIGKILL)
		# os.killpg(process_chrome.pid, signal.SIGTERM)
		except Exception as error:
			logging.info(error)

		ret_fd.close()