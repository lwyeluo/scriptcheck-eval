# coding=utf-8

import os

from result_handler.finalResultForFrames import FinalResultListForFrames
from result_handler.finalResult import FinalResultList
from result_handler.parseLog import ParseLog
from result_handler.parseDomain import ParseDomain
from result_handler import _topsites_dir, _topsites_china_dir


class Parse(object):
	def __init__(self, result_dir):
		self._results_dir = os.path.join(result_dir, "results")
		print(self._results_dir)

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
				web_page_data.append(parser.getVulnWebPage())

				# parse the domain
				parser_domain = ParseDomain(webpage_filename, domain=domain, url=webpage.replace(",", "/"))
				frames_data.append(parser_domain.getFramesInfo())

				# if parser_domain.getFramesInfo().getRestrictedSetDomains():
				# 	return web_page_data, frames_data

		return web_page_data, frames_data


def run(type):
	webpages, frames = None, None
	if type == "China":
		webpages, frames = Parse(_topsites_china_dir).run()
	elif type == "Alexa":
		webpages, frames = Parse(_topsites_dir).run()
	else:
		raise Exception("Bad argument. Use China or Alexa")

	# log
	output = FinalResultList(webpages)
	# output.printRawDataTable()
	output.printDistributionTable()
	output.printDistributionTableWithJSStack()
	output.printDistributionTableWithDiffFeatures()
	output.printInfoOfVulnWebpages()

	# log
	output = FinalResultListForFrames(frames)
	output.print()

