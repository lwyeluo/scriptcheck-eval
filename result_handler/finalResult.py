# coding=utf-8

from result_handler.vulnWebPage import VulnWebPage
from result_handler import _logger


class FinalResultList(object):
	def __init__(self, results):
		self._results = results
		self._log = _logger
		# the distribution of frame chains
		self._dist_frame_chain = {}  # {sizeOfFrameChain: Webpages}
		self._dist_frame_chain_with_stack = {}  # {sizeOfFrameChain: Webpages}
		self._dist_frame_chain_with_diff_feature = {}  # {sizeOfCrossOriginFrameChain: Webpages}
		# webpages which has vuln frame chain after we consider the js stack and features
		self._webpages_with_vuln_frame_chain = {}  # {url: {'filename': filename, 'length': length}
		# number of tested webpages
		self._tested_webpages = 0

		self.compute()

	def compute(self):
		for i, ret in enumerate(self._results):
			# ret is an instance of |VulnWebPage|
			if type(ret) is not VulnWebPage:
				raise Exception("Bad format for a VulnWebPage")

			if not ret.reachable:
				continue

			url = ret.url if ret.url != "" else ret.domain

			# compute _dist_frame_chain
			length = ret.len_for_vuln_frame_chain
			if length in self._dist_frame_chain:
				self._dist_frame_chain[length].append(url)
			else:
				self._dist_frame_chain[length] = [url]

			# compute _dist_frame_chain_with_stack
			length = ret.len_for_vuln_frame_chain_with_stack
			if length > 1:
				if length in self._dist_frame_chain_with_stack:
					self._dist_frame_chain_with_stack[length].append(url)
				else:
					self._dist_frame_chain_with_stack[length] = [url]

			# compute _dist_frame_chain_with_diff_feature
			length = ret.len_for_vuln_frame_chain_with_diff_features
			if length > 1:
				if length in self._dist_frame_chain_with_diff_feature:
					self._dist_frame_chain_with_diff_feature[length].append(url)
				else:
					self._dist_frame_chain_with_diff_feature[length] = [url]

			# compute _webpages_with_vuln_frame_chain
			length = ret.len_for_vuln_frame_chain_with_diff_features
			if length > 1:
				self._webpages_with_vuln_frame_chain[url] = {
					'filename': ret.file_name,
					'length': str(ret.len_for_vuln_frame_chain_with_diff_features),
					'MaxVulnFrameChain': ret.max_vuln_frame_chain_with_diff_features
				}

			# compute _tested_webpages
			self._tested_webpages += 1

	def printRawDataTable(self):
		# the table for all reachable frames
		self._log.info("\n\n")
		self._log.info("#######################################")
		self._log.info("####      TABLE for RAW DATA       ####")
		self._log.info("#######################################")

		VulnWebPage.printTag()
		for ret in self._results:
			ret.printReachable()

	def printDistributionTable(self):
		self._log.info("\n\n")
		self._log.info("#######################################")
		self._log.info("# TABLE for frame chain distribution  #")
		self._log.info("#######################################")

		self._log.info("length\t#webpages\twebpages")
		keys = sorted(self._dist_frame_chain.keys())
		for k in keys:
			v = self._dist_frame_chain[k]
			d = str(k) + '\t' + str(len(v))  # length\t#webpages
			#d += '\t' + ','.join(v)  # \twebpages
			self._log.info(d)

	def printDistributionTableWithJSStack(self):
		self._log.info("\n\n")
		self._log.info("#######################################################")
		self._log.info("# TABLE for frame chain (with JS stack) distribution  #")
		self._log.info("#######################################################")

		self._log.info("length\t#webpages\twebpages")
		keys = sorted(self._dist_frame_chain_with_stack.keys())
		for k in keys:
			v = self._dist_frame_chain_with_stack[k]
			d = str(k) + '\t' + str(len(v))  # length\t#webpages
			#d += '\t' + ','.join(v)  # \twebpages
			self._log.info(d)

	def printDistributionTableWithDiffFeatures(self):
		self._log.info("\n\n")
		self._log.info("############################################################")
		self._log.info("# TABLE for frame chain (with diff features) distribution  #")
		self._log.info("############################################################")

		self._log.info("length\t#webpages\twebpages")
		keys = sorted(self._dist_frame_chain_with_diff_feature.keys())
		for k in keys:
			v = self._dist_frame_chain_with_diff_feature[k]
			d = str(k) + '\t' + str(len(v))  # length\t#webpages
			#d += '\t' + ','.join(v)  # \twebpages
			self._log.info(d)

	def printInfoOfVulnWebpages(self):
		self._log.info("\n\n")
		self._log.info("#######################################")
		self._log.info("# Information for vuln webpages #")
		self._log.info("#######################################")

		self._log.info('\nUrl\tfilename\tMaxLengthOfFrameChain\tMaxVulnFrameChain')
		for k, v in self._webpages_with_vuln_frame_chain.items():
			d = k + '\t' + v['filename'] + '\t' + v['length']  # url \t filename \t length
			d += '\t' + str(v['MaxVulnFrameChain'])  # \t MaxVulnFrameChain
			self._log.info(d)

		number_of_tested_webpages = len(self._results)
		number_of_vuln_webpages = len(self._webpages_with_vuln_frame_chain)
		self._log.info("\n\nRATE: number_of_vuln_webpages/number_of_tested_webpages = %d, %d, %f%%" %
					   (number_of_vuln_webpages, number_of_tested_webpages,
						number_of_vuln_webpages / number_of_tested_webpages * 100))
