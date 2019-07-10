# coding=utf-8

import os

from result_handler.vulnWebPage import VulnWebPage
from result_handler.finalResult import FinalResultList
from result_handler.parseLog import ParseLog
from result_handler import _result_dir, _top_site_dir


class Parse(object):
	def __init__(self):
		self._results_dir = _result_dir

		self._final_url_filename = os.path.join(_top_site_dir, "final_url")

	def run(self):

		web_page_data = []  # store the final results

		with open(self._final_url_filename, 'r') as f:
			lines = f.readlines()
			for line in lines:

				log = line.strip("\n").split('\t')
				rank, url = log[0], log[1]
				idx = url.find("://")
				if idx >= 0:
					domain = url[idx + 3:]
				else:
					domain = url

				if rank[0] == '#':
					ret = VulnWebPage(domain=domain, reachable=False, rank=rank[1:], url=url)
					web_page_data.append(ret)
					continue

				print("\n\n\t\t[RANK, URL, DOMAIN] = [%s, %s, %s]\n" % (rank, url, domain))

				# load all logs for that domain
				ret_dir = os.path.join(self._results_dir, domain)
				if os.path.exists(ret_dir) and os.path.isdir(ret_dir):
					files = os.listdir(ret_dir)

					# here actually we only have one file. If there are too many files, we need to
					#  change something, do it later!
					if len(files) != 1:
						raise Exception("Now we only support run one test for each webpage")

					for ret_file in files:
						# parse that log
						parser = ParseLog(os.path.join(ret_dir, ret_file), domain=domain,
										  rank=rank, url=url)
						# record the parser result
						web_page_data.append(parser.getVulnWebPage())

			f.close()

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
