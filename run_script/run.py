# coding=utf-8

import logging
import signal
import os
from threading import Timer
from utils.executor import *

from run_script import _chrome_binary, _node_binary, _node_filename, _timeout, _timeout_for_node


class RunUrl(object):
	def __init__(self, url, ret_filename):
		self.url = url  # the url to be loaded
		self.ret_filename = ret_filename  # the file path to save the Chrome's log

		# some features logged by _node_filename
		self.features_completed = '''result: { type: 'string', value: 'complete' }'''
		self.features_collect_frame_info = '''>>> Prepare to get frames's information'''
		self.features_frame_info = "**********"

		# the information for frames
		self.frame_info = {}  # {'parent': {'url': url, 'domain': domain}, 'frameID': {'url': url, 'domain': domain}}

		self.run()

	def timeoutCallback(self, process_node):
		logging.info("\t\tEnter timeoutCallback")
		try:
			os.killpg(process_node.pid, signal.SIGKILL)
		except Exception as error:
			logging.info(error)

	# collect the url and domains for all (same-origin) frames
	def collectInformationForFrames(self, logs):
		# print(logs)
		if self.features_collect_frame_info in logs:
			info = logs[logs.find(self.features_collect_frame_info):].strip('\\n').split('\\n')

			for i in range(1, len(info)):
				data = info[i].strip('\\t')
				if self.features_frame_info in data:
					# parse the information for frame
					child_info = data.split("\\t")
					if len(child_info) != 5:
						logging.info("[ERROR] we failed to parse %s" % data)
						continue
					self.frame_info[child_info[1]] = {
						'url': child_info[2],
						'domain': child_info[3]
					}

	def run(self):
		ret_fd = open(self.ret_filename, 'w')

		print(_chrome_binary)
		process_chrome = subprocess.Popen([_chrome_binary, '--remote-debugging-port=9222'], stderr=ret_fd,
										  stdout=ret_fd)
		logging.info('>>> START ' + self.url)

		time.sleep(10)

		print(_node_binary, _node_filename)
		process_node = subprocess.Popen([_node_binary, _node_filename, self.url, str(_timeout_for_node)], stdout=subprocess.PIPE,
										stderr=subprocess.PIPE, preexec_fn=os.setsid)
		# create a timer
		my_timer = Timer(_timeout, self.timeoutCallback, [process_node])
		my_timer.start()

		stdout, _ = process_node.communicate()
		if self.features_completed in str(stdout):
			logging.info("\t\tweb page [%s] is completed!" % self.url)
		else:
			# print(str(stdout))
			logging.info("\t\tweb page [%s] is TIMEOUT!" % self.url)

		# collect the url and domains for all (same-origin) frames
		self.collectInformationForFrames(str(stdout))

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