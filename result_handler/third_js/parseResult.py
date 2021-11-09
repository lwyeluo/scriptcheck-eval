# coding=utf-8

import os
import pickle
import math
import json

from result_handler.finalResultForFrames import FinalResultListForFrames
from result_handler.finalResult import FinalResultList
from result_handler.third_js.parseLog import ParseLog
from result_handler.parseDomain import ParseDomain
from result_handler import _topsites_dir, _topsites_china_dir
from utils.globalDefinition import _tmp_dir
from utils.regMatch import matchRawDomainFromURL, getSiteFromURL
from utils.logger import _logger


__COOKIE__ = "cookie"
__DOM__ = "dom"


class Parse(object):
	def __init__(self, result_dir):
		self._raw_domains_file = os.path.join(result_dir, "reachable_domains")
		if not os.path.exists(self._raw_domains_file):
			raise Exception("SHOULD have %s" % self._raw_domains_file)

		self._results_dir = os.path.join(result_dir, "results")
		self._results_raw_file = os.path.join(result_dir, "block_results_raw")
		self._results_host_file = os.path.join(result_dir, "block_results_host")
		self._results_third_file = os.path.join(result_dir, "block_results_third")
		print(self._results_dir, self._results_raw_file, self._results_host_file, self._results_third_file)

		# save the site -> rank
		self._site_rank = {}  # {site: rank}
		self._rank_site = {}  # {rank: site}
		self.get_site_rank()

		# save the results
		self._total_res = {}  # {domain: {host_url: {third_url: {__COOKIE__: Y/N, __DOM__: Y/N}}}

		self._log = _logger

	def get_site_rank(self):
		with open(self._raw_domains_file, "r") as fd:
			lines = fd.readlines()
			for i, line in enumerate(lines):
				data = line.strip("\n").split("\t")
				if len(data) != 2:
					raise Exception("Bad format for %s" % self._raw_domains_file)

				# rank, url = int(data[0]), data[1]
				rank, url = i + 1, data[1]
				site = getSiteFromURL(url)
				if site is None:
					raise Exception("Bad format for %s. cannot found site %s"
									% (self._raw_domains_file, url))

				self._site_rank[site] = rank
				self._rank_site[rank] = site

	def handle_result(self, paser_log_res):
		res_cookie, res_dom = paser_log_res
		print(res_cookie, res_dom)

		# handle cookie
		for host_url in res_cookie.keys():
			site = getSiteFromURL(host_url)
			if site is None or site not in self._site_rank.keys():
				continue

			if site not in self._total_res.keys():
				self._total_res[site] = {}

			if host_url not in self._total_res[site].keys():
				self._total_res[site][host_url] = {}

			for third_url in res_cookie[host_url]:
				if third_url not in self._total_res[site][host_url].keys():
					self._total_res[site][host_url][third_url] = {__COOKIE__: False, __DOM__: False}

				self._total_res[site][host_url][third_url][__COOKIE__] = True

		# handle dom
		for host_url in res_dom.keys():
			site = getSiteFromURL(host_url)
			if site is None or site not in self._site_rank.keys():
				continue

			if site not in self._total_res.keys():
				self._total_res[site] = {}

			if host_url not in self._total_res[site].keys():
				self._total_res[site][host_url] = {}

			for third_url in res_dom[host_url]:
				if third_url not in self._total_res[site][host_url].keys():
					self._total_res[site][host_url][third_url] = {__COOKIE__: False, __DOM__: False}

				self._total_res[site][host_url][third_url][__DOM__] = True

	def my_print(self, fd, data):
		print(data, end="")
		fd.write("%s" % data)

	def print_raw_data(self, fd):
		self.my_print(fd, "#######################################\n")
		self.my_print(fd, "# Recorded Raw Data #\n")
		self.my_print(fd, "#######################################\n")

		self.my_print(fd, "RANK\tSITE\tHOST_URL\tTHIRD_URL\tCOOKIE\tDOM\n")
		for rank in sorted(self._rank_site.keys()):
			site = self._rank_site[rank]
			if site not in self._total_res.keys():
				continue

			tag = "%d\t%s\t" % (rank, site)
			self.my_print(fd, tag)
			s_i, s_len = False, len(tag) - 2

			for host_url in self._total_res[site].keys():
				if s_i:
					# self.my_print(fd, " " * s_len)
					self.my_print(fd, "\t" * 2)
				s_i = True

				self.my_print(fd, "%s\t" % host_url)
				h_i, h_s = False, len(host_url) + len(tag) - 3

				for third_url in self._total_res[site][host_url]:
					if h_i:
						# self.my_print(fd, " " * h_s)
						self.my_print(fd, "\t" * 3)
					h_i = True
					cookie = self._total_res[site][host_url][third_url][__COOKIE__]
					dom = self._total_res[site][host_url][third_url][__DOM__]
					data = third_url + "\t"
					data += "Y" if cookie else "N"
					data += "\t"
					data += "Y" if dom else "N"
					data += "\n"
					self.my_print(fd, data)

	def print_host_info(self, fd):
		self.my_print(fd, "#######################################\n")
		self.my_print(fd, "# Recorded host Info #\n")
		self.my_print(fd, "#######################################\n")

		self.my_print(fd, "RANK\tSITE\t#THIRD_URL-cookie\t#THIRD_DOMAIN-cookie\t#THIRD_URL-DOM\t#THIRD_DOMAIN-DOM\n")
		for rank in sorted(self._rank_site.keys()):
			site = self._rank_site[rank]
			if site not in self._total_res.keys():
				continue

			tag = "%d\t%s\t" % (rank, site)
			self.my_print(fd, tag)

			set_cookie_third_url = set()
			set_cookie_third_domain = set()
			set_dom_third_url = set()
			set_dom_third_domain = set()
			for host_url in self._total_res[site].keys():
				for third_url in self._total_res[site][host_url]:
					third_domain = getSiteFromURL(third_url)
					if third_domain is None:
						continue

					cookie = self._total_res[site][host_url][third_url][__COOKIE__]
					dom = self._total_res[site][host_url][third_url][__DOM__]
					if cookie:
						set_cookie_third_url.add(third_url)
						set_cookie_third_domain.add(third_domain)
					if dom:
						set_dom_third_url.add(third_url)
						set_dom_third_domain.add(third_domain)

			info = "%d\t%d\t%d\t%d\n" % (len(set_cookie_third_url),
										 len(set_cookie_third_domain),
										 len(set_dom_third_url),
										 len(set_dom_third_domain))
			self.my_print(fd, info)

	def print_third_info(self, fd):
		self.my_print(fd, "#######################################\n")
		self.my_print(fd, "# Recorded third Info #\n")
		self.my_print(fd, "#######################################\n")

		self.my_print(fd, "RANK\tSITE\t#THIRD_URL-cookie\t#THIRD_DOMAIN-cookie\t#THIRD_URL-DOM\t#THIRD_DOMAIN-DOM\n")

	def finally_compute(self):
		with open(self._results_raw_file, 'w') as fd:
			self.print_raw_data(fd)

		with open(self._results_host_file, 'w') as fd:
			self.print_host_info(fd)

		with open(self._results_third_file, 'w') as fd:
			self.print_third_info(fd)

	def run(self):

		web_page_data = []  # store the final results for webpage
		frames_data = []  # store the final results for frame, including the domains and urls for all frames

		domains = os.listdir(self._results_dir)
		for domain in domains:
			domain_dir = os.path.join(self._results_dir, domain)
			if not os.path.isdir(domain_dir):
				raise Exception("Bad file structure")

			print("\n\n\t\t[DOMAIN] = [%s]\n" % domain)

			webpages = os.listdir(domain_dir)
			for webpage in webpages:
				webpage_filename = os.path.join(domain_dir, webpage)

				# parse that log
				parser = ParseLog(webpage_filename, domain=domain, url=webpage.replace(",", "/"))
				# record the parser result
				self.handle_result(parser.get_result())

		return web_page_data, frames_data


def run():
	p = Parse(_topsites_dir)
	p.run()
	p.finally_compute()

def test():
	from result_handler.third_js.parseLog import test
	test()
