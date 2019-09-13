# coding=utf-8

import os
import pickle
import math

from result_handler.finalResultForFrames import FinalResultListForFrames
from result_handler.finalResult import FinalResultList
from result_handler.parseLog import ParseLog
from result_handler.parseDomain import ParseDomain
from result_handler import _topsites_dir, _topsites_china_dir
from utils.globalDefinition import _tmp_dir
from utils.regMatch import matchRawDomainFromURL, getSiteFromURL
from utils.logger import _logger


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

def runAndSaveObject(type):
	print(">>> runAndSaveObject")
	webpages, frames = None, None
	if type == "China":
		webpages, frames = Parse(_topsites_china_dir).run()
	elif type == "Alexa":
		webpages, frames = Parse(_topsites_dir).run()
	else:
		raise Exception("Bad argument. Use China or Alexa")

	# save objects
	step = 5000
	interval = math.ceil(len(webpages)/step)
	for i in range(0, interval):
		r = (i + 1) * step if i != interval - 1 else len(webpages)
		print("write: %d->%d" % (i*step, r))
		path = os.path.join(_tmp_dir, "webpages-%d.obj" % i)
		with open(path, "wb") as file:
			pickle.dump(webpages[i*step:r], file)

		path = os.path.join(_tmp_dir, "frames-%d.obj" % i)
		with open(path, "wb") as file:
			pickle.dump(frames[i*step:r], file)


def loadAndParseResult():
	print(">>> loadAndParseResult")
	# load objects
	#  each frame in `frames` is an instance of `FinalResultForFrames`
	webpages, frames = [], []
	i = 0
	while True:
		path = os.path.join(_tmp_dir, "webpages-%d.obj" % i)
		if not os.path.exists(path):
			break

		print("load %s" % path)
		with open(path, "rb") as file:
			webpages += pickle.load(file)

		path = os.path.join(_tmp_dir, "frames-%d.obj" % i)
		with open(path, "rb") as file:
			frames += pickle.load(file)

		i += 1

	# print the frame structures
	from result_handler.further_analyze.frame_structure import printFrameStructures
	printFrameStructures(frames, _logger)

	# print the maximum frame chain
	from result_handler.further_analyze.max_frame_chain import MaximumFrameChain
	MaximumFrameChain(webpages, _logger).run()


	# # log
	# output = FinalResultList(webpages)
	# # output.printRawDataTable()
	# output.printDistributionTable()
	# output.printDistributionTableWithJSStack()
	# output.printDistributionTableWithDiffFeatures()
	# output.printInfoOfVulnWebpages()
	#
	# output = FinalResultListForFrames(frames)
	# output.print()

