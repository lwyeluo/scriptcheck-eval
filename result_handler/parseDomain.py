# coding=utf-8

import os
from utils.regMatch import matchPrincipal
from result_handler.finalResultForFrames import FinalResultForFrames


class ParseDomain(object):
	def __init__(self, file_name, domain, url='', rank=-1, is_debug=False):
		self.domain = domain
		self.url = url
		self.rank = rank
		self.file_name = file_name

		# some indicators
		self.feature_new_frame = ">>> [Key] add a new principal. [cid, principal, url, frame_id] = "
		self.feature_set_domain = ">>> Document::setDomain. [old, new] = "

		# save the results
		self.results = {}

		self.handle()

	def handleNewFrame(self, log):
		line = log[log.index(self.feature_new_frame):]
		_, _, remain = line.partition("=")

		info = remain.split(", ")
		if len(info) != 4:
			raise Exception("Bad format: %s" % remain)

		# omit the chrome-search://
		if info[2] == '' or info[2].startswith("chrome-search://"):
			return

		frame_info = matchPrincipal(info[1])
		if not frame_info:
			raise Exception("Bad format when matching principal: %s" % remain)

		self.results[self.file_name]['frames'].append({
			'url': info[2].strip(' '),
			'process_id': frame_info['process_id'],
			'id': frame_info['id'],
			'origin': frame_info['origin']
		})

	def handleSetDomain(self, log):
		line = log[log.index(self.feature_set_domain):]
		_, _, remain = line.partition("=")

		info = remain.split(", ")
		if len(info) != 2:
			raise Exception("Bad format: %s" % remain)

		self.results[self.file_name]['setDomains'].append({
			'old': info[0],
			'new': info[1]
		})

	def handle(self):
		if not os.path.isfile(self.file_name):
			return None

		print(">>> HANDLER %s " % self.file_name)

		self.results[self.file_name] = {
			'frames': [],
			"setDomains": [],
		}

		with open(self.file_name, 'r', encoding="ISO-8859-1") as f:

			content = f.readlines()
			for line in content:
				log = line.strip('\n')

				if self.feature_new_frame in log:
					self.handleNewFrame(log)
				elif self.feature_set_domain in log:
					self.handleSetDomain(log)

			f.close()

		print(self.results)

	def getFramesInfo(self):
		return FinalResultForFrames(domain=self.domain, url=self.url,
								   filepath=self.file_name,
								   data=self.results[self.file_name])

def test():
	ParseDomain()


