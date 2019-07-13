# coding=utf-8

import os
from result_handler.frameChain import FrameChain
from result_handler.vulnWebPage import VulnWebPage


class ParseLog(object):
	def __init__(self, file_name, domain, url='', rank=-1, is_debug=False):
		self.domain = domain
		self.url = url
		self.rank = rank
		self.file_name = file_name

		# some indicators
		self._feature_frame_chain = "updated frame chain: [num, frameChain, subject, last, " \
									"function_name, source_code] = "
		self._feature_metadata = "metadata is [subject_url, domain, routing_id, frame_chain_length," \
								 " parent_origin, parent_domain, parent_routing_id] = "
		self._feature_js_stack = ">>> BindingSecurity::PrintStack. stack is "
		self._feature_set_domain = ">>> Document::setDomain. [old, new] = "

		# save the results
		self.vuln_frames = []  # the frame chain whose size >= 2
		self.max_len_of_frame_chain = 0  # the max length of frame chains

		# the content in that log
		self.content = None
		# the current line index for parsing
		self.idx = -1

		self.is_debug = is_debug

		# parse information from that log
		self.handle()
		# compute the |VulnWebPage|
		self.vuln_web_page = self.compute()

	def getVulnWebPage(self):
		return self.vuln_web_page

	def completeCurrentFrameChain(self, chain, frame_chain):
		frame_chain.recordChain(chain)

	def handleFeatureMetadata(self, line, frame_chain, has_collected_metadata):
		if has_collected_metadata:
			# the metadata has been collected, but we find another metadata
			#  meaning that the previous one is not correct
			frame_chain.removeTail()
		line = line[line.index(self._feature_metadata):]
		_, _, remain = line.partition("=")
		if remain == "":
			raise Exception("Bad format for metadata: " + line)

		# get the subject url and domain
		info = remain.split('", ')
		url = info[0][2:]
		domain = info[1][1:]

		if url.find("chrome-search://") == 0:
			return False

		remain = info[2]
		info = remain.split(',')
		if len(info) != 5:
			raise Exception("Bad format for metadata: " + line)

		frame_info = {
			'url': url,
			'domain': domain,
			'id': info[0].strip(' ').strip('"'),
			'parent_origin': info[2].strip(' ').strip('"'),
			'parent_domain': info[3].strip(' ').strip('"').strip('\n'),
			'parent_id': info[4].strip(' ').strip('"').strip('\n'),
		}

		frame_chain.append(frame_info)

		return True

	def handleFeatureJSStack(self, line, frame_chain):
		stack = []
		while True:
			self.idx += 1
			next_line = self.content[self.idx]
			if self._feature_frame_chain in next_line:
				self.idx -= 1
				break

			if next_line == '\n':
				break

			stack.append(next_line.strip('\n').strip('\t').strip(' '))

		frame_chain.recordJSStack(stack)

	def handleFeatureSetDomain(self, line, frame_chain, has_collected_metadata):
		if not has_collected_metadata:
			raise Exception("You are setting domain before collecting metadata. line is " + line)

		line = line[line.index(self._feature_set_domain):]
		_, _, remain = line.partition("=")
		if remain == "":
			raise Exception("Bad format for setting domain: " + line)

		info = remain.split(',')
		if len(info) != 2:
			raise Exception("Bad format for setting domain: " + line)

		old_domain = info[0].strip('\n').strip(' ').strip('"')
		new_domain = info[1].strip('\n').strip(' ').strip('"')

		frame_chain.updateTail({
			'set_domain': new_domain,
			# here the webpage exploits the Chrome's vuln in document.domain
			'is_domain_vuln': (len(new_domain) > len(old_domain))
		})

	def handleFeatureFrameChain(self, line, frame_chain):

		chain = ""

		if self.is_debug:
			print(">>> begin, line is: %s" % self.content[self.idx])

		# handle all frames in that series of frame chain
		invalid_frame_chain = False
		while self.idx < self.length - 1:
			line = line[line.index(self._feature_frame_chain):]
			_, _, remain = line.partition("=")
			if remain == "":
				raise Exception("Bad format for frame chain: " + line)

			info = remain.split(',')
			chain_len = int(info[0].strip(' '))

			# here is the next series of frame chain, so we should complete the
			#  current one and decrease self.idx with 1
			if chain_len == 1 and (invalid_frame_chain or not frame_chain.isEmpty()):
				break

			chain = info[1].strip(' ')

			# here we begin to update the current series of frame chain

			# 1. collect the metadata and JS stack
			has_collected_metadata = False
			while self.idx < self.length - 1:
				self.idx += 1
				line = self.content[self.idx]

				# here we are in the next frame in current series frame chain
				if self._feature_frame_chain in line:
					break

				if invalid_frame_chain:
					continue

				# get the metadata and JS stack for that frame
				if self._feature_metadata in line:
					if self.handleFeatureMetadata(line, frame_chain, has_collected_metadata):
						has_collected_metadata = True
					else:
						invalid_frame_chain = True
				elif self._feature_js_stack in line:
					self.handleFeatureJSStack(line, frame_chain)
				# if we set domain at that moment
				elif self._feature_set_domain in line:
					self.handleFeatureSetDomain(line, frame_chain, has_collected_metadata)

			if not invalid_frame_chain and not has_collected_metadata and self.idx >= self.length - 1:
				return

		# here is |the end of the log| or |the end of the current series of frame chain|
		if len(frame_chain.frames) > 1:
			print("!!!!!!!!" + chain + "\n\t\t" + str(frame_chain.frames) + "\n\n")
		if not invalid_frame_chain:
			self.completeCurrentFrameChain(chain, frame_chain)
		if self.idx != self.length - 1:
			self.idx -= 1

		if self.is_debug:
			print(">>> end, line is: %s" % self.content[self.idx])

	def handle(self):
		print(">>> HANDLE %s" % self.file_name)
		f = open(self.file_name, "r", encoding="ISO-8859-1")

		self.content = f.readlines()
		self.idx, self.length = -1, len(self.content)
		while self.idx < self.length - 1:
			self.idx += 1
			line = self.content[self.idx].strip("\n")

			# here is a frame chain
			if self._feature_frame_chain in line:

				# extract the series of frame chain in that line
				chain = FrameChain()
				self.handleFeatureFrameChain(line, chain)

				if chain.isEmpty():
					continue

				# update the max size of frame chain
				if chain.length() > self.max_len_of_frame_chain:
					self.max_len_of_frame_chain = chain.length()
				# for frame chain whose size is 1, we ignore it
				if chain.length() < 2:
					continue
				# record frame chain whose size >= 2
				frames = chain.getFramesInfo()
				self.vuln_frames.append({
					'frames': frames,
					'chain': chain.getChain()
				})

		f.close()

	def hasJSStack(self, frame):
		return 'js_stack' in frame.keys() and frame['js_stack']

	# when two frames in a frame chain have different features
	def hasDifferentFeatures(self, frame0, frame1):

		# Feature 1: they have different effective domains
		domain0, domain1 = frame0['domain'], frame1['domain']
		# if frame0 has set its domain, update domain0
		if 'set_domain' in frame0.keys():
			if frame0['is_domain_vuln']:
				return True
			domain0 = frame0['set_domain']

		if domain0 != domain1:
			return True

		# Feature 2: they have different parent frames but not the parent-child relationship
		parent_id0, parent_id1 = frame0['parent_id'], frame1['parent_id']
		id0, id1 = frame0['id'], frame1['id']
		if id0 == parent_id1 or id1 == parent_id0:
			# here means that one is the other's parent frame
			return False

		parent_origin0, parent_origin1 = frame0['parent_origin'], frame1['parent_origin']
		parent_domain0, parent_domain1 = frame0['parent_domain'], frame1['parent_domain']

		print(parent_origin0, ", ", parent_origin1)
		print(parent_domain0, ", ", parent_domain1)
		if parent_origin0 == '' or parent_origin1 == '':
			# here one of them is the top frame
			domain = parent_domain0 + parent_domain1
			return self.domain not in domain

		# if parent_origin0 != parent_origin1:
		# 	return True

		if parent_domain0 != parent_domain1:
			return True

		return False

	# compute the derived information for frame chains, i.e. the |VulnWebPage|
	def compute(self):
		webpage = VulnWebPage(domain=self.domain, reachable=True, rank=self.rank, url=self.url)

		# append the file name
		webpage.appendResultFileName(self.file_name)

		# append the vuln frame chains
		webpage.appendVulnFrameChain(self.vuln_frames)

		# compute the |vuln_frame_chain_with_stack|
		vuln_frame_chain_with_stack = []
		for frame_chain in self.vuln_frames:
			for frame in frame_chain['frames']:
				if self.hasJSStack(frame):
					vuln_frame_chain_with_stack.append(frame_chain)
					break

		webpage.appendVulnFrameChainWithJSStack(vuln_frame_chain_with_stack)

		# compute the |vuln_frame_chain_with_diff_features|
		vuln_frame_chain_with_diff_features = []
		for frame_chain in vuln_frame_chain_with_stack:
			for i in range(0, len(frame_chain['frames']) - 1):
				# get the two consecutive frames
				frame0 = frame_chain['frames'][i]
				frame1 = frame_chain['frames'][i+1]

				# whether they has different features
				if self.hasDifferentFeatures(frame0, frame1) and self.hasJSStack(frame1):
					if self.is_debug:
						print("\n!!!! We found a vuln frame chain: %s, %s\n" % (str(frame0), str(frame1)))
					vuln_frame_chain_with_diff_features.append(frame_chain)
					break

		webpage.appendVulnFrameChainWithDiffFeatures(vuln_frame_chain_with_diff_features)

		# compute by webpage itself
		webpage.compute()

		print("\tThe length is ", webpage.len_for_vuln_frame_chain, webpage.len_for_vuln_frame_chain_with_stack,
			  webpage.len_for_vuln_frame_chain_with_diff_features)

		return webpage


def test(domain="yahoo.com"):
	from result_handler import _result_alexa_dir

	ret_dir = os.path.join(_result_alexa_dir, domain)
	if os.path.exists(ret_dir) and os.path.isdir(ret_dir):
		files = os.listdir(ret_dir)
		for ret_file in files:
			parser = ParseLog(os.path.join(ret_dir, ret_file), domain=domain, is_debug=True)
			webpage = parser.getVulnWebPage()
			print(webpage.len_for_vuln_frame_chain)
			print(webpage.len_for_vuln_frame_chain_with_stack)
			print(webpage.len_for_vuln_frame_chain_with_diff_features)

def test_log(log_file_name, domain):
	parser = ParseLog(log_file_name, domain=domain, is_debug=True)
	webpage = parser.getVulnWebPage()
	print(webpage.len_for_vuln_frame_chain)
	print(webpage.len_for_vuln_frame_chain_with_stack)
	print(webpage.len_for_vuln_frame_chain_with_diff_features)
