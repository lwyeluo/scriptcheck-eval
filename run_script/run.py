# coding=utf-8


import signal
import os
from threading import Timer
from utils.executor import *

from utils.globalDefinition import _chrome_binary, _node_binary, _timeout, _timeout_for_node
from utils.globalDefinition import _node_filename, _node_run_url_filename


class RunUrl(object):
	def __init__(self, url, ret_filename, node_filename=_node_filename,
				 timeout=_timeout, timeout_for_node=_timeout_for_node,
				 chrome_binary=_chrome_binary):
		self.url = url  # the url to be loaded
		self.ret_filename = ret_filename  # the file path to save the Chrome's log

		self.chrome_binary_ = chrome_binary

		self.node_filename = node_filename
		self.timeout = timeout
		self.timeout_for_node = timeout_for_node

		# some features logged by _node_filename
		self.features_completed = '''result: { type: 'string', value: 'complete' }'''
		self.features_collect_frame_info = '''>>> Prepare to get frames's information'''
		self.features_frame_info = "**********"

		# the information for frames
		self.frame_info = {}  # {'parent': {'url': url, 'domain': domain}, 'frameID': {'url': url, 'domain': domain}}

		self.flag = self.run()

	def timeoutCallback(self, process_node):
		print("\t\tEnter timeoutCallback")
		try:
			os.killpg(process_node.pid, signal.SIGKILL)
		except Exception as error:
			print(error)

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
						print("[ERROR] we failed to parse %s" % data)
						continue
					self.frame_info[child_info[1]] = {
						'url': child_info[2],
						'domain': child_info[3]
					}

	def run(self):
		flag = 0  # 0: completed, 1: timeout
		ret_fd = open(self.ret_filename, 'w')

		print(self.chrome_binary_)
		process_chrome = subprocess.Popen([self.chrome_binary_, '--remote-debugging-port=9222'], stderr=ret_fd,
										  stdout=ret_fd)
		print('>>> START ' + self.url)

		time.sleep(5)

		print(_node_binary, self.node_filename)
		process_node = subprocess.Popen([_node_binary, self.node_filename, self.url, str(self.timeout_for_node)],
										stdout=subprocess.PIPE,
										stderr=subprocess.PIPE, preexec_fn=os.setsid)
		# create a timer
		my_timer = Timer(self.timeout, self.timeoutCallback, [process_node])
		my_timer.start()

		stdout, _ = process_node.communicate()
		if self.features_completed in str(stdout):
			print("\t\tweb page [%s] is completed!" % self.url)
			flag = 0
		else:
			# print(str(stdout))
			print("\t\tweb page [%s] is TIMEOUT!" % self.url)
			flag = 1

		# collect the url and domains for all (same-origin) frames
		if self.node_filename == _node_filename:
			self.collectInformationForFrames(str(stdout))

		print('>>> FINISH ' + self.url)

		my_timer.cancel()

		time.sleep(2)
		# kill chrome
		try:
			print("\t>>> kill Chrome [%d]" % process_chrome.pid)
			os.kill(process_chrome.pid, signal.SIGKILL)
		# os.killpg(process_chrome.pid, signal.SIGTERM)
		except Exception as error:
			print(error)

		ret_fd.close()

		return flag
