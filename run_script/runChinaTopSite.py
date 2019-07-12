# coding=utf-8

import logging
import os
from utils.executor import *
from run_script.run import RunUrl

from run_script import _result_log_dir_for_china, _dir
from top_sites_china import _max_webpage_in_one_domain


class TimTest(object):
	def __init__(self, machine_index):

		self._results_dir = _result_log_dir_for_china

		self._top_site_dir = os.path.join(os.path.dirname(_dir), "top_sites_china")
		self._raw_domain_filename = os.path.join(self._top_site_dir, "topsites")
		self._webpage_dir = os.path.join(self._top_site_dir, "result")

		self._split_dir = os.path.join(self._top_site_dir, "domain-split")
		self._domain_filename = os.path.join(self._split_dir, "sites-%d" % machine_index)

		self.machine_index = machine_index

		# create an EMPTY directory to save results
		execute("rm -rf " + self._results_dir + " || true")
		execute("mkdir -p " + self._results_dir + " || true")

	def runPerDomain(self, domain, url_file_name):
		logging.info("\n\n\t\t[DOMAIN] = [%s]\n" % domain)

		# create the directory for results
		ret_dir = self._results_dir + "/" + domain
		execute("mkdir -p " + ret_dir)

		# list all urls
		with open(url_file_name, 'r') as f_url:
			urls = f_url.readlines()
			for i in range(0, len(urls)):

				# for each domain, we only handle the maximum webpages
				if i >= _max_webpage_in_one_domain:
					break

				url = urls[i].strip('\n').strip(' ')

				# run that url
				filename = url.replace('/', ',')
				if len(filename) > 20:
					filename = filename[:20]
				RunUrl(url, ret_dir + "/" + filename)

			f_url.close()

	def run(self):
		print(">>> domain file name is " + self._domain_filename)
		with open(self._domain_filename, 'r') as f:
			lines = f.readlines()
			for line in lines:
				domain = line.strip("\n").strip(' ')

				# open the file containing urls for that domain
				url_file_name = os.path.join(self._webpage_dir, domain)
				if not os.path.isfile(url_file_name):
					raise Exception("We cannot find url for " + domain)

				self.runPerDomain(domain, url_file_name)

			f.close()


def run(machine_index):
	TimTest(machine_index).run()

