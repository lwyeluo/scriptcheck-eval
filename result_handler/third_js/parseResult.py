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
from utils.regMatch import matchRawDomainFromURL, getSiteFromURL, strip_into_csv
from utils.logger import _logger


__COOKIE_GET__ = "cookie_get"
__COOKIE_SET__ = "cookie_set"
__DOM__ = "dom"
__XHR__ = "xhr"


class Parse(object):
	def __init__(self, result_dir):
		self._raw_domains_file = os.path.join(result_dir, "reachable_domains")
		if not os.path.exists(self._raw_domains_file):
			raise Exception("SHOULD have %s" % self._raw_domains_file)

		self._results_dir = os.path.join(result_dir, "results")
		self._results_raw_file = os.path.join(result_dir, "block_results_raw.csv")
		self._results_host_file = os.path.join(result_dir, "block_results_host.csv")
		self._results_third_file = os.path.join(result_dir, "block_results_third.csv")
		self._results_host_dom_file = os.path.join(result_dir, "block_results_host_dom.csv")
		self._results_target_dom_file = os.path.join(result_dir, "block_results_dom_key.csv")
		print(self._results_dir, self._results_raw_file, self._results_host_file, self._results_third_file)

		# save the site -> rank
		self._site_rank = {}  # {site: rank}
		self._rank_site = {}  # {rank: site}
		self.get_site_rank()

		self.dom_type_ = ["<input", "<form", "<button"]
		self.dom_feature_ = ["passwd", "password", "secret", "credential",
							 "card", "privacy", "private", "security"]

		# save the results
		self._total_res = {}  # {domain: {host_url: {third_url: {__COOKIE_GET__: Y/N, __DOM__: {keyword: []}, __XHR__: []}}}

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

	def handle_result_for_cookie(self, res_cookie, cookie_type):
		if cookie_type != __COOKIE_SET__ and cookie_type != __COOKIE_GET__:
			raise Exception("BAD args")
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
					self._total_res[site][host_url][third_url] = {
						__COOKIE_GET__: False, __COOKIE_SET__: False, __DOM__: {}, __XHR__: set()
					}

				self._total_res[site][host_url][third_url][cookie_type] = True

	def get_key_word_for_dom(self, dom_info):
		if not isinstance(dom_info, str):
			return None, None
		if dom_info == "":
			return None, None
		if not dom_info.startswith("<") and dom_info.find("->") > 0:
			return dom_info[:dom_info.find("->")], None
		if not dom_info.startswith("<") or not dom_info.endswith(">"):
			return None, None
		# check type
		keyword_type = None
		for t in self.dom_type_:
			if dom_info.find(t) == 0:
				keyword_type = t
				break

		# check word
		keyword = None
		for fea in self.dom_feature_:
			if dom_info.find(fea) > 1:  # should not be "<Fea"
				keyword = fea
				break
		return keyword_type, keyword

	def handle_result_for_dom(self, res_dom):
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
					self._total_res[site][host_url][third_url] = {
						__COOKIE_GET__: False, __COOKIE_SET__: False, __DOM__: {}, __XHR__: set()
					}

				for dom_info in res_dom[host_url][third_url]:
					keyword_type, keyword = self.get_key_word_for_dom(dom_info)
					for k in [keyword_type, keyword]:
						if k:
							if k not in self._total_res[site][host_url][third_url][__DOM__].keys():
								self._total_res[site][host_url][third_url][__DOM__][k] = set()
							self._total_res[site][host_url][third_url][__DOM__][k].add(dom_info)

	def handle_result_for_xhr(self, res_xhr):
		for host_url in res_xhr.keys():
			site = getSiteFromURL(host_url)
			if site is None or site not in self._site_rank.keys():
				continue

			if site not in self._total_res.keys():
				self._total_res[site] = {}

			if host_url not in self._total_res[site].keys():
				self._total_res[site][host_url] = {}

			for third_url in res_xhr[host_url]:
				if third_url not in self._total_res[site][host_url].keys():
					self._total_res[site][host_url][third_url] = {
						__COOKIE_GET__: False, __COOKIE_SET__: False, __DOM__: {}, __XHR__: set()
					}

				for request_url in res_xhr[host_url][third_url]:
					self._total_res[site][host_url][third_url][__XHR__].add(request_url)

	def handle_result(self, paser_log_res):
		res_cookie_get, res_cookie_set, res_dom, res_xhr = paser_log_res
		print(res_cookie_get, res_cookie_set, res_dom, res_xhr)

		# handle cookie
		self.handle_result_for_cookie(res_cookie_get, __COOKIE_GET__)
		self.handle_result_for_cookie(res_cookie_set, __COOKIE_SET__)

		# handle dom
		self.handle_result_for_dom(res_dom)

		# handle xhr
		self.handle_result_for_xhr(res_xhr)

	def my_print(self, fd, data):
		print(data, end="")
		fd.write("%s" % data)

	def print_raw_data(self, fd):
		self.my_print(fd, "RANK,SITE,HOST_URL,THIRD_URL,COOKIE_GET,COOKIE_SET,DOM,DOM_INFO,NET,REQUEST_URL\n")
		for rank in sorted(self._rank_site.keys()):
			site = self._rank_site[rank]
			if site not in self._total_res.keys():
				continue

			tag = '%d,"%s,' % (rank, strip_into_csv(site))
			self.my_print(fd, tag)
			s_i, s_len = False, len(tag) - 2

			for host_url in self._total_res[site].keys():
				if s_i:
					# self.my_print(fd, " " * s_len)
					self.my_print(fd, "," * 2)
				s_i = True

				self.my_print(fd, '%s,' % strip_into_csv(host_url))
				h_i, h_s = False, len(host_url) + len(tag) - 3

				for third_url in self._total_res[site][host_url]:
					if h_i:
						# self.my_print(fd, " " * h_s)
						self.my_print(fd, "," * 3)
					h_i = True
					cookie_get = self._total_res[site][host_url][third_url][__COOKIE_GET__]
					cookie_set = self._total_res[site][host_url][third_url][__COOKIE_SET__]
					dom = self._total_res[site][host_url][third_url][__DOM__]
					xhr = self._total_res[site][host_url][third_url][__XHR__]
					data = third_url + ","
					data += "Y" if cookie_get else "N"
					data += ","
					data += "Y" if cookie_set else "N"
					data += ","
					if dom:
						data += "Y,"
						for idx, keyword in enumerate(dom.keys()):
							data += strip_into_csv("%s:" % keyword)
							data += strip_into_csv('\r\n'.join(dom[keyword]))
							if idx != len(dom.keys()) - 1:
								data += strip_into_csv("\r\n")
					else:
						data += "N,"
					data += ","
					if xhr:
						data += "Y," + strip_into_csv('\r\n'.join(xhr))
					else:
						data += "N,"
					data += "\n"
					self.my_print(fd, data)

	def print_host_info(self, fd):
		self.my_print(fd, "RANK,SITE,"
						  "#THIRD_URL-cookie-get,#THIRD_DOMAIN-cookie-get,"
						  "#THIRD_URL-cookie-set,#THIRD_DOMAIN-cookie-set,"
						  "#THIRD_URL-DOM,#THIRD_DOMAIN-DOM,"
						  "#THIRD_URL-NET,#THIRD_DOMAIN-NET\n")
		for rank in sorted(self._rank_site.keys()):
			site = self._rank_site[rank]
			if site not in self._total_res.keys():
				continue

			tag = '%d,%s,' % (rank, strip_into_csv(site))
			self.my_print(fd, tag)

			get_cookie_third_url, get_cookie_third_domain = set(), set()
			set_cookie_third_url, set_cookie_third_domain = set(), set()
			set_dom_third_url, set_dom_third_domain = set(), set()
			set_xhr_third_url, set_xhr_third_domain = set(), set()
			for host_url in self._total_res[site].keys():
				for third_url in self._total_res[site][host_url]:
					third_domain = getSiteFromURL(third_url)
					if third_domain is None:
						continue

					cookie_get = self._total_res[site][host_url][third_url][__COOKIE_GET__]
					cookie_set = self._total_res[site][host_url][third_url][__COOKIE_SET__]
					dom = self._total_res[site][host_url][third_url][__DOM__]
					xhr = self._total_res[site][host_url][third_url][__XHR__]
					if cookie_get:
						get_cookie_third_url.add(third_url)
						get_cookie_third_domain.add(third_domain)
					if cookie_set:
						set_cookie_third_url.add(third_url)
						set_cookie_third_domain.add(third_domain)
					if dom:
						set_dom_third_url.add(third_url)
						set_dom_third_domain.add(third_domain)
					if xhr:
						set_xhr_third_url.add(third_url)
						set_xhr_third_domain.add(third_domain)

			info = "%d,%d,%d,%d,%d,%d,%d,%d\n" % (len(get_cookie_third_url), len(get_cookie_third_domain),
												  len(set_cookie_third_url), len(set_cookie_third_domain),
												  len(set_dom_third_url), len(set_dom_third_domain),
												  len(set_xhr_third_url), len(set_xhr_third_domain))
			self.my_print(fd, info)

	def print_third_info(self, fd):
		_dict_3rd = {}  # {third_site: {__COOKIE_GET__: {host_site}, __DOM__: {host_site}, __XHR__: {host_site}}

		for rank in sorted(self._rank_site.keys()):
			site = self._rank_site[rank]
			if site not in self._total_res.keys():
				continue

			for host_url in self._total_res[site].keys():
				for third_url in self._total_res[site][host_url]:
					third_domain = getSiteFromURL(third_url)
					if third_domain is None:
						continue

					cookie_get = self._total_res[site][host_url][third_url][__COOKIE_GET__]
					cookie_set = self._total_res[site][host_url][third_url][__COOKIE_SET__]
					dom = self._total_res[site][host_url][third_url][__DOM__]
					xhr = self._total_res[site][host_url][third_url][__XHR__]
					if not cookie_get and not cookie_set and not dom:
						continue

					if third_domain not in _dict_3rd.keys():
						_dict_3rd[third_domain] = {
							__COOKIE_GET__: set(), __COOKIE_SET__: set(), __DOM__: set(), __XHR__: set()
						}
					if cookie_get:
						_dict_3rd[third_domain][__COOKIE_GET__].add(site)
					if cookie_set:
						_dict_3rd[third_domain][__COOKIE_SET__].add(site)
					if dom:
						_dict_3rd[third_domain][__DOM__].add(site)
					if xhr:
						_dict_3rd[third_domain][__XHR__].add(site)

		self.my_print(fd, "THIRD_DOMAIN,#HOST_SITE-cookie-get,#HOST_SITE-cookie-set,#HOST_SITE-DOM,#HOST_SITE-NET\n")
		for third_domain in _dict_3rd.keys():
			data = '%s,%d,%d,%d,%d' % (strip_into_csv(third_domain),
									   len(_dict_3rd[third_domain][__COOKIE_GET__]),
									   len(_dict_3rd[third_domain][__COOKIE_SET__]),
									   len(_dict_3rd[third_domain][__DOM__]),
									   len(_dict_3rd[third_domain][__XHR__]))
			self.my_print(fd, "%s\n" % data)

	def print_host_dom(self, fd):
		self.my_print(fd, "RANK,SITE")
		dom_type_list = sorted(self.dom_type_)
		dom_feature_list = sorted(self.dom_feature_)
		for dom_type in dom_type_list:
			self.my_print(fd, ",TYPE_%s" % dom_type)
		for dom_fea in dom_feature_list:
			self.my_print(fd, ",WORD_%s" % dom_fea)
		self.my_print(fd, "\n")

		for rank in sorted(self._rank_site.keys()):
			site = self._rank_site[rank]
			if site not in self._total_res.keys():
				continue

			info = {}
			for dom_type in dom_type_list:
				info[dom_type] = 0
			for dom_word in dom_feature_list:
				info[dom_word] = 0

			valid_dom = False
			for host_url in self._total_res[site].keys():
				for third_url in self._total_res[site][host_url]:
					third_domain = getSiteFromURL(third_url)
					if third_domain is None:
						continue

					dom = self._total_res[site][host_url][third_url][__DOM__]
					if not dom:
						continue

					for k in dom.keys():
						info[k] += 1
						valid_dom = True

			if valid_dom:
				data = '%d,%s,' % (rank, strip_into_csv(site))
				for dom_type in dom_type_list:
					data += "%d," % info[dom_type]
				for dom_word in dom_feature_list:
					data += "%d," % info[dom_word]
				data += "\n"
				self.my_print(fd, data)

	def print_target_dom(self, fd):
		dom_type_list = sorted(self.dom_type_)
		dom_feature_list = sorted(self.dom_feature_)
		keys = dom_type_list + dom_feature_list

		info = {}  # {keyword: {third_url: [], host_url: []}}
		info_key_third, info_key_third_domain = "third_url", "third_domain"
		info_key_host, info_key_host_domain = "host_url", "host_domain"
		for k in keys:
			info[k] = {info_key_third: set(), info_key_host: set(),
					   info_key_third_domain: set(), info_key_host_domain: set()}

		for rank in sorted(self._rank_site.keys()):
			site = self._rank_site[rank]
			if site not in self._total_res.keys():
				continue

			for host_url in self._total_res[site].keys():
				for third_url in self._total_res[site][host_url]:
					third_domain = getSiteFromURL(third_url)
					if third_domain is None:
						continue

					dom = self._total_res[site][host_url][third_url][__DOM__]
					if not dom:
						continue

					for k in dom.keys():
						info[k][info_key_third].add(third_url)
						info[k][info_key_host].add(host_url)
						info[k][info_key_third_domain].add(third_domain)
						info[k][info_key_host_domain].add(site)

		self.my_print(fd, "DOM_KEY,#THIRD_URL,#THIRD_DOMAIN,#HOST_URL,#HOST_DOAMIN\n")
		for k in keys:
			data = '%s,%d,%d,%d,%d' % (k, len(info[k][info_key_third]),
									   len(info[k][info_key_third_domain]),
									   len(info[k][info_key_host]),
									   len(info[k][info_key_host_domain]))
			self.my_print(fd, "%s\n" % data)

	def finally_compute(self):
		with open(self._results_raw_file, 'w') as fd:
			self.print_raw_data(fd)

		with open(self._results_host_file, 'w') as fd:
			self.print_host_info(fd)

		with open(self._results_third_file, 'w') as fd:
			self.print_third_info(fd)

		with open(self._results_host_dom_file, 'w') as fd:
			self.print_host_dom(fd)

		with open(self._results_target_dom_file, 'w') as fd:
			self.print_target_dom(fd)

	def run(self):
		domains = os.listdir(self._results_dir)
		for domain in domains:
			domain_dir = os.path.join(self._results_dir, domain)
			if not os.path.isdir(domain_dir):
				continue

			print("\n\n\t\t[DOMAIN] = [%s]\n" % domain)

			webpages = os.listdir(domain_dir)
			for webpage in webpages:
				webpage_filename = os.path.join(domain_dir, webpage)

				# parse that log
				parser = ParseLog(webpage_filename, domain=domain, url=webpage.replace(",", "/"), need_check=True)
				# record the parser result
				self.handle_result(parser.get_result())


def run():
	p = Parse(_topsites_dir)
	p.run()
	p.finally_compute()

def test():
	from result_handler.third_js.parseLog import test
	test()
