# coding=utf-8

import os
from result_handler.frameChain import FrameChain
from result_handler.vulnWebPage import VulnWebPage
from utils.logger import _logger


class ParseLog(object):
	def __init__(self, file_name, domain, url='', rank=-1, is_debug=False):
		self.domain = domain
		self.url = url
		self.rank = rank
		self.file_name = file_name

		# some indicators
		self._feature_dom_block = '''"The task does not have the permission to access the DOM [url, info, is_task_sensitive] = '''
		self._feature_cookie_block = '''"The task does not have the permission to access the cookie. [host url] = '''
		self._feature_js_obj_block = '''"Uncaught SecurityError: Blocked risky world from accessing normal world", source:'''

		# save the results
		self._res_cookie = {}  # {host_url: [third_url]}
		self._res_dom = {}  # {host_url: [third_url]}
		self._res_js = {}  # {host_url: [third_url]} -> TODO

		# the content in that log
		self.content = None
		# the current line index for parsing
		self.idx = -1

		self.is_debug = is_debug

		# parse information from that log
		self.handle()

	def get_result(self):
		return self._res_cookie, self._res_dom

	def handle(self):
		print(">>> HANDLE %s" % self.file_name)
		f = open(self.file_name, "r", encoding="ISO-8859-1")

		self.content = f.readlines()
		self.idx, self.length = -1, len(self.content)
		while self.idx < self.length - 1:
			self.idx += 1
			line = self.content[self.idx].strip("\n")

			if self._feature_cookie_block in line:
				# handle cookie
				'''e.g., [9835:9835:1107/011016.248111:INFO:CONSOLE(7)] "The task does not have the permission to access the cookie. 
				[host url] = https://nypost.com/sitemap/, ", source: https://cdn.parsely.com/keys/nypost.com/p.js (7)'''
				_, _, d = line.rpartition(self._feature_cookie_block)
				first, _, last = d.rpartition('''", source: ''')
				host_url, _, _ = first.partition(''',''')
				_, _, last = last.rpartition(''',''')
				third_url, _, _ = last.partition(''' (''')
				if host_url not in self._res_cookie.keys():
					self._res_cookie[host_url] = set()
				self._res_cookie[host_url].add(third_url)

			elif self._feature_dom_block in line:
				# handle dom
				'''[23017: 23017:1107 / 233021.992513: INFO:CONSOLE(2)] "The task does not have the permission to access the DOM
				 [url, info, is_task_sensitive] = https://login.kataweb.it/login/common/api/sso-frame.jsp?v=1&appId=repubblica.it&targetDomain=https%3A//www.repubblica.it&enableLogs=undefined, 
				 <slot name="user-agent-custom-assign-slot"></slot>, 1", source: 
				 https://www.repstatic.it/cless/common/stable/js/vendor/jquery/jquery-1.8.2.min.js (2)'''
				_, _, d = line.rpartition(self._feature_dom_block)
				first, _, last = d.rpartition('''", source: ''')
				host_url, _, _ = first.partition(''',''')
				_, _, last = last.rpartition(''',''')
				third_url, _, _ = last.partition(''' (''')
				if host_url not in self._res_dom.keys():
					self._res_dom[host_url] = set()
				self._res_dom[host_url].add(third_url)

			elif self._feature_js_obj_block in line:
				# handle js
				pass

		f.close()


def test():
	from result_handler import _topsites_dir

	domain = "repubblica.it"
	ret_dir = os.path.join(os.path.join(_topsites_dir, "results"), domain)
	log_file = os.path.join(ret_dir, "https___www_repubblica_it_viaggi_")
	parser = ParseLog(log_file, domain=domain, is_debug=True)


def test_log(log_file_name, domain):
	parser = ParseLog(log_file_name, domain=domain, is_debug=True)
	webpage = parser.getVulnWebPage()
	print(webpage.len_for_vuln_frame_chain)
	print(webpage.len_for_vuln_frame_chain_with_stack)
	print(webpage.len_for_vuln_frame_chain_with_diff_features)
