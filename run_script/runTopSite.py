# coding=utf-8

import logging
import os
from utils.executor import *
from run_script.run import RunUrl

from run_script import _result_log_dir, _dir, outputAtConsole


class TimTest(object):
	def __init__(self):

		self._results_dir = _result_log_dir

		self._top_site_dir = os.path.join(os.path.dirname(_dir), "top_sites")
		self._final_url_filename = os.path.join(self._top_site_dir, "final_url")

		# for each web page, we run 3 rounds
		self._round = 3
		self._timeout = 60

		# create an EMPTY directory to save results
		execute("rm -rf " + self._results_dir + " || true")
		execute("mkdir -p " + self._results_dir + " || true")

	def run(self):
		with open(self._final_url_filename, 'r') as f:
			lines = f.readlines()
			for line in lines:
				if line[0] == '#':
					continue
				log = line.strip("\n").split('\t')
				rank, url = log[0], log[1]
				domain = url[url.index("://") + 3:]
				logging.info("\n\n\t\t[RANK, URL, DOMAIN] = [%s, %s, %s]\n" % (rank, url, domain))

				# create the directory for results
				ret_dir = self._results_dir + "/" + domain
				execute("mkdir -p " + ret_dir)

				# run that url
				for i in range(0, self._round):
					RunUrl(url, ret_dir + "/" + getTime())
			f.close()


def run():
	outputAtConsole()
	TimTest().run()

