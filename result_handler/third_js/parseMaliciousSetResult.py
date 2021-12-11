# coding=utf-8

import os
import pickle
import math
import json

from result_handler.finalResultForFrames import FinalResultListForFrames
from result_handler.finalResult import FinalResultList
from result_handler.third_js.parseLog import ParseLog
from result_handler.parseDomain import ParseDomain
from result_handler import _malicious_set_dir
from utils.globalDefinition import _tmp_dir
from utils.globalDefinition import _chrome_binary_normal, _chrome_binary, _chrome_binary_name
from utils.regMatch import matchRawDomainFromURL, getSiteFromURL, strip_into_csv
from utils.logger import _logger
from utils.executor import *


__COOKIE_GET__ = "cookie_get"
__COOKIE_SET__ = "cookie_set"
__DOM__ = "dom"
__XHR__ = "xhr"


class Parse(object):
	def __init__(self, result_dir, chrome_type=_chrome_binary):
		self._chrome_type = chrome_type
		chrome_type_name = _chrome_binary_name[chrome_type]

		self._third_server_addr = "http://third-party.com:3001/"
		self._test_html_rel = "taskPermission/scriptChecker/malicious-set/js-malicious-dataset"

		# manually analyzed
		self._manually_analyze_file = os.path.join(result_dir, "manually_analyzed.json")
		self._manually_results = self.load_manually_analyzed_file()

		self._results_dir = os.path.join(result_dir, "results-%s" % chrome_type_name)
		self._results_fail_file = os.path.join(result_dir, "benign_or_fail_js.csv")
		self._results_raw_file = os.path.join(result_dir, "block_results_raw.csv")
		self._results_host_file = os.path.join(result_dir, "block_results_host.csv")
		self._results_third_file = os.path.join(result_dir, "block_results_third.csv")
		print(self._results_dir, self._results_raw_file, self._results_host_file, self._results_third_file)

		# save the site -> rank
		self._site_rank = {}  # {site: rank}
		self._rank_site = {}  # {rank: site}

		self.dom_type_ = ["<input", "<form", "<button"]
		self.dom_feature_ = ["passwd", "password", "secret", "credential",
							 "card", "privacy", "private", "security"]

		# save the results
		self._total_res = {}  # {domain: {host_url: {third_url: {__COOKIE_GET__: Y/N, __DOM__: Y/N}}}
		self._total_failed_js = set()
		self._total_parsed_js = set()
		self._total_benign_js = set()
		self._untracked_source_js = set()

		self._log = _logger

	def load_manually_analyzed_file(self):
		with open(self._manually_analyze_file, "r") as fp:
			input_data = json.load(fp)
		return input_data

	def my_print(self, fd, data):
		print(data, end="")
		fd.write("%s" % data)

	def handle_result_for_cookie(self, res_cookie, script, cookie_type):
		if cookie_type != __COOKIE_SET__ and cookie_type != __COOKIE_GET__:
			raise Exception("BAD args")

		valid = False
		for host_url in res_cookie.keys():
			site = matchRawDomainFromURL(host_url)
			if site is None:
				continue

			if site not in self._total_res.keys():
				self._total_res[site] = {}

			if host_url not in self._total_res[site].keys():
				self._total_res[site][host_url] = {}

			for third_url in res_cookie[host_url]:
				if "jquery.min.js" in third_url or third_url.endswith(".html"):
					continue

				script_url = script if third_url == "" else third_url
				script_url = self.strip_js_filepath(script_url)

				if script_url not in self._total_res[site][host_url].keys():
					self._total_res[site][host_url][script_url] = {
						__COOKIE_GET__: False, __COOKIE_SET__: False, __DOM__: {}, __XHR__: set()
					}

				self._total_res[site][host_url][script_url][cookie_type] = True
				valid = True
		return valid

	def get_key_word_for_dom(self, dom_info):
		if not isinstance(dom_info, str):
			return None, None
		if dom_info == "":
			return None, None
		if not dom_info.startswith("<") and dom_info.find("->") > 0:
			return dom_info[:dom_info.find("->")], None
		if not dom_info.startswith("<") or not dom_info.endswith(">"):
			return None, None
		# get type
		info, _, _ = dom_info.partition(" ")
		return info[1:], None

	def handle_result_for_dom(self, res_dom, script):
		valid = False
		for host_url in res_dom.keys():
			site = matchRawDomainFromURL(host_url)
			if site is None:
				continue

			if site not in self._total_res.keys():
				self._total_res[site] = {}

			if host_url not in self._total_res[site].keys():
				self._total_res[site][host_url] = {}

			for third_url in res_dom[host_url]:
				if "jquery.min.js" in third_url or third_url.endswith(".html"):
					continue

				script_url = script if third_url == "" else third_url
				script_url = self.strip_js_filepath(script_url)

				if script_url not in self._total_res[site][host_url].keys():
					self._total_res[site][host_url][script_url] = {
						__COOKIE_GET__: False, __COOKIE_SET__: False, __DOM__: {}, __XHR__: set()
					}

				for dom_info in res_dom[host_url][third_url]:
					keyword_type, keyword = self.get_key_word_for_dom(dom_info)
					for k in [keyword_type, keyword]:
						if k:
							if k not in self._total_res[site][host_url][script_url][__DOM__].keys():
								self._total_res[site][host_url][script_url][__DOM__][k] = set()
							self._total_res[site][host_url][script_url][__DOM__][k].add(dom_info)
							valid = True
		return valid

	def handle_result_for_xhr(self, res_xhr, script):
		valid = False
		for host_url in res_xhr.keys():
			site = matchRawDomainFromURL(host_url)
			if site is None:
				continue

			if site not in self._total_res.keys():
				self._total_res[site] = {}

			if host_url not in self._total_res[site].keys():
				self._total_res[site][host_url] = {}

			for third_url in res_xhr[host_url]:
				if "jquery.min.js" in third_url or third_url.endswith(".html"):
					continue

				script_url = script if third_url == "" else third_url
				script_url = self.strip_js_filepath(script_url)

				if script_url not in self._total_res[site][host_url].keys():
					self._total_res[site][host_url][script_url] = {
						__COOKIE_GET__: False, __COOKIE_SET__: False, __DOM__: {}, __XHR__: set()
					}

				for request_url in res_xhr[host_url][third_url]:
					self._total_res[site][host_url][script_url][__XHR__].add(request_url)
					valid = True
		return valid

	def handle_result(self, paser_log_res, script):
		res_cookie_get, res_cookie_set, res_dom, res_xhr = paser_log_res
		print(res_cookie_get, res_cookie_set, res_dom, res_xhr)

		# the third_url is "", meaning that there may be malicious code running in eval
		for u in [res_cookie_get, res_cookie_set, res_dom, res_xhr]:
			for h in u.keys():
				for t in u[h]:
					if t == "":
						self._untracked_source_js.add(self.strip_js_filepath(script))

		valid = False
		# handle cookie
		if self.handle_result_for_cookie(res_cookie_get, script, __COOKIE_GET__):
			valid = True
		if self.handle_result_for_cookie(res_cookie_set, script, __COOKIE_SET__):
			valid = True

		# handle dom
		if self.handle_result_for_dom(res_dom, script):
			valid = True

		# handle xhr
		if self.handle_result_for_xhr(res_xhr, script):
			valid = True
		return valid

	def print_raw_data(self, fd):
		self.my_print(fd, "SITE,HOST_URL,THIRD_URL,COOKIE_GET,COOKIE_SET,DOM,DOM_INFO,NET,REQUEST_URL\n")
		for site in sorted(self._total_res.keys()):
			tag = "%s," % site
			self.my_print(fd, tag)
			s_i, s_len = False, len(tag) - 2

			for host_url in sorted(self._total_res[site].keys()):
				if s_i:
					# self.my_print(fd, " " * s_len)
					self.my_print(fd, ",")
				s_i = True

				self.my_print(fd, '%s,' % strip_into_csv(host_url))
				h_i, h_s = False, len(host_url) + len(tag) - 3

				for third_url in sorted(self._total_res[site][host_url]):
					if h_i:
						# self.my_print(fd, " " * h_s)
						self.my_print(fd, "," * 2)
					h_i = True
					cookie_get = self._total_res[site][host_url][third_url][__COOKIE_GET__]
					cookie_set = self._total_res[site][host_url][third_url][__COOKIE_SET__]
					dom = self._total_res[site][host_url][third_url][__DOM__]
					xhr = self._total_res[site][host_url][third_url][__XHR__]
					data = self.strip_js_filepath(third_url) + ","
					data += "Y" if cookie_get else "N"
					data += ","
					data += "Y" if cookie_set else "N"
					data += ","
					if dom:
						data += "Y,"
						for idx, keyword in sorted(enumerate(dom.keys())):
							data += strip_into_csv("%s:" % keyword)
							data += strip_into_csv('\r\n'.join(sorted(dom[keyword])))
							if idx != len(dom.keys()) - 1:
								data += strip_into_csv("\r\n")
					else:
						data += "N,"
					data += ","
					if xhr:
						data += "Y," + strip_into_csv('\r\n'.join(sorted(xhr)))
					else:
						data += "N,"
					data += "\n"
					self.my_print(fd, data)

	def print_third_info(self, fd):
		_dict_3rd = {}  # {third_site: {__COOKIE_GET__: {host_site}, __DOM__: {host_site}, __XHR__: {host_site}}

		for site in sorted(self._total_res.keys()):
			print(">>>> site", site)
			if site != "host.com:3001":
				continue

			for host_url in sorted(self._total_res[site].keys()):
				for third_url in sorted(self._total_res[site][host_url]):
					third_domain = getSiteFromURL(third_url)
					print(">>>> third", third_domain, third_url)
					if third_domain is None or not third_domain.endswith("com:3001"):
						continue

					# get the malicious script name
					js_name = self.strip_js_filepath(third_url)

					cookie_get = self._total_res[site][host_url][third_url][__COOKIE_GET__]
					cookie_set = self._total_res[site][host_url][third_url][__COOKIE_SET__]
					dom = self._total_res[site][host_url][third_url][__DOM__]
					xhr = self._total_res[site][host_url][third_url][__XHR__]
					if not cookie_get and not cookie_set and not dom:
						continue

					if js_name not in _dict_3rd.keys():
						_dict_3rd[js_name] = {
							__COOKIE_GET__: set(), __COOKIE_SET__: set(), __DOM__: set(), __XHR__: set()
						}
					if cookie_get:
						_dict_3rd[js_name][__COOKIE_GET__].add(site)
					if cookie_set:
						_dict_3rd[js_name][__COOKIE_SET__].add(site)
					if dom:
						_dict_3rd[js_name][__DOM__].add(site)
					if xhr:
						_dict_3rd[js_name][__XHR__].add(site)

		self.my_print(fd, "THIRD_NAME,#HOST_SITE-cookie-get,#HOST_SITE-cookie-set,#HOST_SITE-DOM,#HOST_SITE-NET\n")
		found = False
		for i in range(0, 1000):
			js_name = "js_%d.txt.js" % i
			if js_name not in _dict_3rd.keys():
				continue
			found = True
			data = '"%s",%d,%d,%d,%d' % (strip_into_csv(js_name), len(_dict_3rd[js_name][__COOKIE_GET__]),
										 len(_dict_3rd[js_name][__COOKIE_SET__]),
										 len(_dict_3rd[js_name][__DOM__]),
										 len(_dict_3rd[js_name][__XHR__]))
			self.my_print(fd, "%s\n" % data)

		if not found:
			for js_name in sorted(_dict_3rd.keys()):
				data = '"%s",%d,%d,%d,%d' % (strip_into_csv(js_name), len(_dict_3rd[js_name][__COOKIE_GET__]),
											 len(_dict_3rd[js_name][__COOKIE_SET__]),
											 len(_dict_3rd[js_name][__DOM__]),
											 len(_dict_3rd[js_name][__XHR__]))
				self.my_print(fd, "%s\n" % data)

	def strip_js_filepath(self, path):
		if not isinstance(path, str):
			return path
		idx = path.find(self._test_html_rel)
		if idx > 0:
			return path[idx + len(self._test_html_rel):]
		idx = path.find(self._results_dir)
		if idx == 0:
			return path[idx + len(self._results_dir):]
		return path

	def print_fail_file(self, fd):
		self.my_print(fd, "Succeed to run: %d\n" % len(self._total_parsed_js))
		self.my_print(fd, "Failed to run: %d\n" % len(self._total_failed_js))
		self.my_print(fd, "Benign: %d\n" % len(self._total_benign_js))
		self.my_print(fd, "Benign Scripts:")
		for js in sorted(self._total_benign_js):
			# get results
			js_name = self.strip_js_filepath(js)
			for k in sorted(self._manually_results.keys()):
				if js_name.find(k) >= 0:
					reason = strip_into_csv(self._manually_results[k])
					self.my_print(fd, ",%s,%s\n" % (js_name, reason))
					break
			else:
				self.my_print(fd, ",%s\n" % self.strip_js_filepath(js))
		if len(self._total_benign_js) == 0:
			self.my_print(fd, "\n")

		self.my_print(fd, "No-source-error Scripts:")
		for js in sorted(self._untracked_source_js):
			self.my_print(fd, ",%s\n" % self.strip_js_filepath(js))
		if len(self._untracked_source_js) == 0:
			self.my_print(fd, "\n")

		self.my_print(fd, "Failed Scripts:")
		for js in sorted(self._total_failed_js):
			self.my_print(fd, ",%s\n" % self.strip_js_filepath(js))
		pass

	def finally_compute(self):
		with open(self._results_fail_file, 'w') as fd:
			self.print_fail_file(fd)

		with open(self._results_raw_file, 'w') as fd:
			self.print_raw_data(fd)

		# with open(self._results_third_file, 'w') as fd:
		# 	self.print_third_info(fd)

	def check_run_error(self, path):
		f = open(path, "r", encoding="ISO-8859-1")
		for line in f.readlines():
			if line.find(", source:") > 0:
				for d in ["Uncaught ReferenceError:", "Uncaught TypeError:", "Uncaught SyntaxError"]:
					if d in line:
						f.close()
						return False
		f.close()
		return True

	def run(self):
		web_page_data = []  # store the final results for webpage
		frames_data = []  # store the final results for frame, including the domains and urls for all frames
		self._total_failed_js = set()
		self._total_parsed_js = set()
		self._total_benign_js = set()

		years = os.listdir(self._results_dir)
		for year in sorted(years):
			p = os.path.join(self._results_dir, year)
			if not os.path.isdir(p):
				continue

			cmd = ["find", p, "-name", "*.js"]
			print(cmd)
			files = executeByList(cmd)
			for i, script in enumerate(sorted(files.split("\n"))):
				if not os.path.isfile(script):
					continue

				if not self.check_run_error(script):
					self._total_failed_js.add(script)
					continue

				self._total_parsed_js.add(script)

				print("\n\n\t\t[PATH] = [%s]\n" % script)

				# parse that log
				parser = ParseLog(script, domain="host.com", need_check=False)
				# record the parser result
				if not self.handle_result(parser.get_result(), script):
					self._total_benign_js.add(script)

		return web_page_data, frames_data

	def test(self):
		ret_dir = os.path.join(_malicious_set_dir, "results")
		log_file = os.path.join(ret_dir, "RIG ek/ek_rig_start[.]remax-grandrapidstwp[.]com.js")
		if not os.path.exists(log_file):
			print(">>> run input")
		parser = ParseLog(log_file, domain="host.com:3001", is_debug=True)
		self.handle_result(parser.get_result(), log_file)
		print(self._total_res)


def run():
	p = Parse(_malicious_set_dir)
	p.run()
	p.finally_compute()

def test():
	p = Parse(_malicious_set_dir)
	p.test()
