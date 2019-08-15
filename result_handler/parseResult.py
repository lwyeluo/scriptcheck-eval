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

	# log
	print("The size of frames is %d" % len(frames))
	cross_site_frames, cross_origin_frames = 0, 0
	embeded_sites = {}  # url: sites
	i = 0
	for frame in frames:
		structure = frame.getFrameStructure()
		if len(structure) <= 1:
			continue
		origin_set = set()
		for s in structure.values():
			domain = matchRawDomainFromURL(s)
			if domain:
				origin_set.add(s)
		if len(origin_set) == 1:
			continue
		cross_origin_frames += 1
		site_set = set()
		for origin in origin_set:
			site = getSiteFromURL(origin)
			if site:
				site_set.add(site)
		if len(site_set) == 1:
			continue
		cross_site_frames += 1

		# record the embeded sites
		_, _, main_site = os.path.dirname(frame.filepath).rpartition('/')
		if main_site not in site_set:
			continue

		site_set.remove(main_site)
		if main_site not in embeded_sites.keys():
			embeded_sites[main_site] = site_set
		else:
			[embeded_sites[main_site].add(s) for s in site_set]

	print("total = %d, cross-origin = %d (%f%%), cross-site = %d (%f%%), sites with cross-sites iframes=%d" %
		  (len(frames), cross_origin_frames, cross_origin_frames/len(frames), cross_site_frames, cross_site_frames/len(frames),
		   len(embeded_sites.keys())))

	_logger.info("################################################")
	_logger.info("\t\t\tRaw Data\t\t")
	_logger.info("################################################")
	for site, embdeds in embeded_sites.items():
		_logger.info("%s\t%d\t%s" % (site, len(embdeds), ','.join(embdeds)))

	_logger.info("################################################")
	_logger.info("\t\t\tDistribution for main frame\t\t")
	_logger.info("################################################")
	distri_main = {}
	for site, embdeds in embeded_sites.items():
		if len(embdeds) not in distri_main.keys():
			distri_main[len(embdeds)] = [site]
		else:
			distri_main[len(embdeds)].append(site)
	_logger.info("#numberOfEmbdeddedSites\t#numberOfMainSites\tMainSites")
	for l in sorted(distri_main.keys()):
		_logger.info("%d\t%d\t%s" % (l, len(distri_main[l]), ','.join(distri_main[l])))

	_logger.info("################################################")
	_logger.info("\t\t\tDistribution for embedded frame\t\t")
	_logger.info("################################################")
	collect_embed = {}
	for site, embdeds in embeded_sites.items():
		for e in embdeds:
			if e not in collect_embed.keys():
				collect_embed[e] = [site]
			else:
				collect_embed[e].append(site)
	distri_embed = {}
	for embed, sites in collect_embed.items():
		if len(sites) not in distri_embed.keys():
			distri_embed[len(sites)] = [embed]
		else:
			distri_embed[len(sites)].append(embed)
	_logger.info("#numberOfMainSites\t#numberOfEmbeddedSites\tEmbedSites")
	for l in sorted(distri_embed.keys()):
		_logger.info("%d\t%d\t%s" % (l, len(distri_embed[l]), ','.join(distri_embed[l])))


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

