# coding = utf-8

from result_handler import _logger


class VulnWebPage(object):
	def __init__(self, domain='', reachable=False, rank=-1, url=''):
		self.domain = domain
		self.reachable = reachable
		self.rank = rank
		self.url = url

		# the frame chains whose length is bigger than 1
		self.vuln_frame_chain = []
		# the frame chains, which belong to |self.vuln_frame_chain| and the corresponding js stack is not null
		self.vuln_frame_chain_with_stack = []
		# the frame chains, which belong to |self.vuln_frame_chain_with_stack| but have different features
		self.vuln_frame_chain_with_diff_features = []

		# the maximum length of frame chains in the above three cases
		self.len_for_vuln_frame_chain = 1
		self.len_for_vuln_frame_chain_with_stack = 0
		self.len_for_vuln_frame_chain_with_diff_features = 0

		# the vuln frame chain with the maximum length
		self.max_vuln_frame_chain_with_diff_features = ''

		self.file_name = ""

	########################################################################################
	#
	#               Methods for SET
	#
	########################################################################################
	def setReachable(self, reachable):
		self.reachable = reachable

	def setRank(self, rank):
		self.rank = rank

	def setUrl(self, url):
		self.url = url

	def setDomain(self, domain):
		self.domain = domain

	########################################################################################
	#
	#               Methods for RECORD
	#
	########################################################################################
	def appendResultFileName(self, filename):
		self.file_name = filename

	def appendVulnFrameChain(self, vuln_frame_chain):
		self.vuln_frame_chain = vuln_frame_chain

	def appendVulnFrameChainWithJSStack(self, vuln_frame_chain_with_stack):
		self.vuln_frame_chain_with_stack = vuln_frame_chain_with_stack

	def appendVulnFrameChainWithDiffFeatures(self, vuln_frame_chain_with_diff_features):
		self.vuln_frame_chain_with_diff_features = vuln_frame_chain_with_diff_features

	########################################################################################
	#
	#               Methods for Compute
	#
	########################################################################################
	def compute(self):
		# self.len_for_vuln_frame_chain = 0
		for frame_chain in self.vuln_frame_chain:
			if len(frame_chain['frames']) > self.len_for_vuln_frame_chain:
				self.len_for_vuln_frame_chain = len(frame_chain['frames'])

		# self.len_for_vuln_frame_chain_with_stack = 0
		for frame_chain in self.vuln_frame_chain_with_stack:
			if len(frame_chain['frames']) > self.len_for_vuln_frame_chain_with_stack:
				self.len_for_vuln_frame_chain_with_stack = len(frame_chain['frames'])

		# self.len_for_vuln_frame_chain_with_diff_features = 0
		for frame_chain in self.vuln_frame_chain_with_diff_features:
			if len(frame_chain['frames']) > self.len_for_vuln_frame_chain_with_diff_features:
				self.len_for_vuln_frame_chain_with_diff_features = len(frame_chain['frames'])
				self.max_vuln_frame_chain_with_diff_features = frame_chain['chain']

	########################################################################################
	#
	#               Methods for PRINT
	#
	########################################################################################
	def print(self):
		data = str(self.rank) + '\t' + self.domain + '\t' + self.url + '\t' + str(self.reachable)
		data += '\t' + str(self.len_for_vuln_frame_chain)
		data += '\t' + str(self.len_for_vuln_frame_chain_with_stack)
		data += '\t' + str(self.len_for_vuln_frame_chain_with_diff_features)
		data += '\t' + self.file_name

		_logger.info(data)

	def printReachable(self):
		if self.reachable:
			self.print()

	@classmethod
	def printTag(cls):
		basic_tag = "rank\tdomain\turl\treachable\tlen_for_vuln_frame_chain\tlen_with_stack\tlen_final\tfilename"
		_logger.info("\n" + basic_tag + "\n")
