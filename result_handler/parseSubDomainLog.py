# coding=utf-8

import re, os


'''
Parse a log file to collect the information of Frames
'''
class ParseSubDomainLog(object):
	def __init__(self):
		self.filepath = None
		self.results = {}

		# features in log
		self.feature_new_frame = ">>> [Key] add a new principal. [cid, principal, url, frame_id] = "
		self.feature_set_domain = ">>> Document::setDomain. [old, new] = "

	'''
		Parse the principal: 5:3_https://blog.csdn.net/
			The format is [processId:routingId_origin]
	'''
	def matchPrincipal(self, principal):
		reg = "(\d{1,}):(\d{1,})_([^\s/]+://[^\s/]+/)(.*)"
		m = re.match(reg, principal)
		if m:
			process_id, routing_id, origin, remain = m.group(1), m.group(2), m.group(3), m.group(4)
			return {
				'process_id': process_id,
				'id': routing_id,
				'origin': origin
			}
		return None

	def handleNewFrame(self, log):
		line = log[log.index(self.feature_new_frame):]
		_, _, remain = line.partition("=")

		info = remain.split(", ")
		if len(info) != 4:
			raise Exception("Bad format: %s" % remain)

		# omit the chrome-search://
		if info[2] == '' or info[2].startswith("chrome-search://"):
			return

		frame_info = self.matchPrincipal(info[1])
		if not frame_info:
			raise Exception("Bad format when matching principal: %s" % remain)

		self.results[self.filepath]['frames'].append({
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

		self.results[self.filepath]['setDomains'].append({
			'old': info[0],
			'new': info[1]
		})

	def run(self, filepath):
		self.filepath = filepath
		if not os.path.isfile(self.filepath):
			return None

		print(">>> HANDLER %s " % self.filepath)

		self.results[self.filepath] = {
			'frames': [],
			"setDomains": [],
		}

		with open(self.filepath, 'r', encoding="ISO-8859-1") as f:

			content = f.readlines()
			for line in content:
				log = line.strip('\n')

				if self.feature_new_frame in log:
					self.handleNewFrame(log)
				elif self.feature_set_domain in log:
					self.handleSetDomain(log)

			f.close()