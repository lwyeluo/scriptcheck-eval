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
from utils.regMatch import matchRawDomainFromURL, getSiteFromURL
from utils.logger import _logger
from utils.executor import *


__COOKIE__ = "cookie"
__DOM__ = "dom"
__XHR__ = "xhr"


class Parse(object):
	def __init__(self, result_dir):
		self._results_dir = os.path.join(result_dir, "results")
		self._results_raw_file = os.path.join(result_dir, "block_results_raw.csv")
		self._results_host_file = os.path.join(result_dir, "block_results_host.csv")
		self._results_third_file = os.path.join(result_dir, "block_results_third.csv")
		print(self._results_dir, self._results_raw_file, self._results_host_file, self._results_third_file)

		# save the site -> rank
		self._site_rank = {}  # {site: rank}
		self._rank_site = {}  # {rank: site}

		# save the results
		self._total_res = {}  # {domain: {host_url: {third_url: {__COOKIE__: Y/N, __DOM__: Y/N}}}

		self._log = _logger

	def my_print(self, fd, data):
		print(data, end="")
		fd.write("%s" % data)

	def handle_result_for_cookie(self, res_cookie):
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

				if third_url not in self._total_res[site][host_url].keys():
					self._total_res[site][host_url][third_url] = {__COOKIE__: False, __DOM__: False, __XHR__: set()}

				self._total_res[site][host_url][third_url][__COOKIE__] = True

	def handle_result_for_dom(self, res_dom):
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

				if third_url not in self._total_res[site][host_url].keys():
					self._total_res[site][host_url][third_url] = {__COOKIE__: False, __DOM__: False, __XHR__: set()}

				self._total_res[site][host_url][third_url][__DOM__] = True

	def handle_result_for_xhr(self, res_xhr):
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

				if third_url not in self._total_res[site][host_url].keys():
					self._total_res[site][host_url][third_url] = {__COOKIE__: False, __DOM__: False, __XHR__: set()}

				for request_url in res_xhr[host_url][third_url]:
					self._total_res[site][host_url][third_url][__XHR__].add(request_url)

	def handle_result(self, paser_log_res):
		res_cookie, res_dom, res_xhr = paser_log_res
		print(res_cookie, res_dom, res_xhr)

		# handle cookie
		self.handle_result_for_cookie(res_cookie)

		# handle dom
		self.handle_result_for_dom(res_dom)

		# handle xhr
		self.handle_result_for_xhr(res_xhr)

	def print_raw_data(self, fd):
		self.my_print(fd, "SITE,HOST_URL,THIRD_URL,COOKIE,DOM,NET\n")
		for site in self._total_res.keys():
			tag = "%s," % site
			self.my_print(fd, tag)
			s_i, s_len = False, len(tag) - 2

			for host_url in self._total_res[site].keys():
				if s_i:
					# self.my_print(fd, " " * s_len)
					self.my_print(fd, ",")
				s_i = True

				self.my_print(fd, "%s," % host_url)
				h_i, h_s = False, len(host_url) + len(tag) - 3

				for third_url in self._total_res[site][host_url]:
					if h_i:
						# self.my_print(fd, " " * h_s)
						self.my_print(fd, "," * 2)
					h_i = True
					cookie = self._total_res[site][host_url][third_url][__COOKIE__]
					dom = self._total_res[site][host_url][third_url][__DOM__]
					xhr = self._total_res[site][host_url][third_url][__XHR__]
					data = third_url + ","
					data += "Y" if cookie else "N"
					data += ","
					data += "Y" if dom else "N"
					data += ","
					if xhr:
						data += "Y," + ','.join(xhr)
					else:
						data += "N,"
					data += "\n"
					self.my_print(fd, data)

	def print_third_info(self, fd):
		_dict_3rd = {}  # {third_site: {__COOKIE__: {host_site}, __DOM__: {host_site}, __XHR__: {host_site}}

		for site in self._total_res.keys():
			print(">>>> site", site)
			if site != "host.com:3001":
				continue

			for host_url in self._total_res[site].keys():
				for third_url in self._total_res[site][host_url]:
					third_domain = getSiteFromURL(third_url)
					print(">>>> third", third_domain, third_url)
					if third_domain is None or not third_domain.endswith("com:3001"):
						continue

					# get the malicious script name
					_, _, js_name = third_url.rpartition("/")

					cookie = self._total_res[site][host_url][third_url][__COOKIE__]
					dom = self._total_res[site][host_url][third_url][__DOM__]
					xhr = self._total_res[site][host_url][third_url][__XHR__]
					if not cookie and not dom:
						continue

					if js_name not in _dict_3rd.keys():
						_dict_3rd[js_name] = {__COOKIE__: set(), __DOM__: set(), __XHR__: set()}
					if cookie:
						_dict_3rd[js_name][__COOKIE__].add(site)
					if dom:
						_dict_3rd[js_name][__DOM__].add(site)
					if xhr:
						_dict_3rd[js_name][__XHR__].add(site)

		self.my_print(fd, "THIRD_NAME,#HOST_SITE-cookie,#HOST_SITE-DOM,#HOST_SITE-NET\n")
		found = False
		for i in range(0, 1000):
			js_name = "js_%d.txt.js" % i
			if js_name not in _dict_3rd.keys():
				continue
			found = True
			data = "%s,%d,%d,%d" % (js_name, len(_dict_3rd[js_name][__COOKIE__]),
									len(_dict_3rd[js_name][__DOM__]),
									len(_dict_3rd[js_name][__XHR__]))
			self.my_print(fd, "%s\n" % data)

		if not found:
			for js_name in sorted(_dict_3rd.keys()):
				data = "%s,%d,%d,%d" % (js_name, len(_dict_3rd[js_name][__COOKIE__]),
										len(_dict_3rd[js_name][__DOM__]),
										len(_dict_3rd[js_name][__XHR__]))
				self.my_print(fd, "%s\n" % data)

	def finally_compute(self):
		with open(self._results_raw_file, 'w') as fd:
			self.print_raw_data(fd)

		with open(self._results_third_file, 'w') as fd:
			self.print_third_info(fd)

	def run(self):
		web_page_data = []  # store the final results for webpage
		frames_data = []  # store the final results for frame, including the domains and urls for all frames

		years = os.listdir(self._results_dir)
		for year in years:
			p = os.path.join(self._results_dir, year)
			if not os.path.isdir(p):
				continue

			cmd = ["find", p, "-name", "*.js"]
			print(cmd)
			files = executeByList(cmd)
			for i, script in enumerate(files.split("\n")):
				if not os.path.isfile(script):
					continue

				print("\n\n\t\t[PATH] = [%s]\n" % script)

				# parse that log
				parser = ParseLog(script, domain="host.com", need_check=False)
				# record the parser result
				self.handle_result(parser.get_result())

		return web_page_data, frames_data


def run():
	p = Parse(_malicious_set_dir)
	p.run()
	p.finally_compute()

def test():
	from result_handler.third_js.parseLog import test
	test()
