# coding=utf-8

import json
import random
import os
import shutil
import time
from utils.globalDefinition import _node_run_url_filename, _cache_for_Chrome_filepath, _node_filename
from utils.globalDefinition import _timeout_benchmark, _timeout_for_node
from run_script.run import RunUrl
from utils.executor import *
from utils.globalDefinition import _random_sample


class RunChrome(object):
	def __init__(self, results_dir, url_list):
		self._results_dir = results_dir
		if os.path.exists(self._results_dir):
			shutil.rmtree(self._results_dir)
		os.mkdir(self._results_dir)

		self._url_list = url_list

		self.test_url = "https://www.baidu.com"

	def run(self):

		i = 0

		for site in self._url_list:
			print(">>>> handle site: ", site)
			results_dir = os.path.join(self._results_dir, site)
			execute("mkdir -p " + results_dir + " || true")

			for url in self._url_list[site]:
				# generate a unique name for the results
				filename = url.replace('/', ',')
				if len(filename) > 30:
					filename = filename[:30]
				filename += ''.join(random.sample(_random_sample, 10))

				print("[url, filename] = %s, %s" % (url, filename))
				RunUrl(url, results_dir + "/" + filename, timeout=60, node_filename=_node_run_url_filename)

				i += 1
				if i % 100 == 0:
					self.clearChrome()

	'''
		Some caches for Chrome must be cleared, otherwise the latency for Chrome is too high
	'''
	def clearChrome(self):
		if os.path.exists(_cache_for_Chrome_filepath):
			shutil.rmtree(_cache_for_Chrome_filepath)

		# run Chrome for the welcome webpage
		print(">>> Welcome to Chrome")
		filepath = os.path.join(self._results_dir, "test")
		RunUrl(self.test_url, filepath, node_filename=_node_run_url_filename)

		time.sleep(5)

class CatchURL(object):

	def __init__(self):

		base_dir = os.path.dirname(os.path.abspath(__file__))
		data_dir = os.path.join(base_dir, "data")
		self.results_dir = os.path.join(base_dir, "results")

		self.tim_eval_dir = os.path.dirname(os.path.dirname(base_dir)) \
							+ "/url_list/topsitesAlexa/urls"

		self.input_file = os.path.join(data_dir, "2mdn")
		self.output_file = os.path.join(data_dir, "2mdn_urls")
		self.data = self.loadData()
		# self.saveUrl()

	def loadData(self):
		sites = {}

		with open(self.input_file, "r") as f:
			for d in f.readlines():
				site = d.strip("\n")
				sites[site] = []

				url_file = os.path.join(self.tim_eval_dir, site)
				if os.path.exists(url_file):
					fp = open(url_file, "r")
					for url in fp.readlines():
						sites[site].append(url.strip("\n"))

		return sites

	def saveUrl(self):
		fp = open(self.output_file, "w")
		json.dump(self.data, fp, indent=2)
		fp.close()

	def run(self):
		p = RunChrome(results_dir=self.results_dir, url_list=self.data)
		p.clearChrome()
		p.run()


def run():
	p = CatchURL()
	p.run()