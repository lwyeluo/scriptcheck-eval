# coding=utf-8

import os

from result_handler.vulnWebPage import VulnWebPage
from result_handler.finalResult import FinalResultList
from result_handler.parseLog import ParseLog
from result_handler import _result_china_dir, _top_site_dir


class Parse(object):
	def __init__(self, result_dir=_result_china_dir):
		self._results_dir = result_dir

	def run(self):

		web_page_data = []  # store the final results

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
				web_page_data.append(parser.getVulnWebPage())

		return web_page_data


def run():
	web_page_data = Parse().run()

	# log
	output = FinalResultList(web_page_data)
	output.printRawDataTable()
	output.printDistributionTable()
	output.printDistributionTableWithJSStack()
	output.printDistributionTableWithDiffFeatures()
	output.printInfoOfVulnWebpages()
