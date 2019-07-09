import os
import logging

from result_handler.finalResult import FinalResult, FinalResultList
from result_handler.parseLog import ParseLog

_dir = os.path.abspath(os.path.dirname(__file__))
_top_site_dir = os.path.join(os.path.dirname(_dir), "top_sites")
_log_filename = os.path.join(os.path.dirname(_dir), "result-parse-log.log")
_result_dir = os.path.join(_dir, "tim-results")
print(_top_site_dir)


def outputAtConsole():
	logging.basicConfig(level=logging.DEBUG, format='%(message)s', filename=_log_filename, filemode="w")

	console = logging.StreamHandler()
	console.setLevel(logging.DEBUG)
	console.setFormatter(logging.Formatter("%(message)s"))
	logging.getLogger('').addHandler(console)


class Parse(object):
	def __init__(self):
		self._results_dir = _result_dir

		self._final_url_filename = os.path.join(_top_site_dir, "final_url")

	def run(self):

		final_results = []  # store the final results

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
					ret = FinalResult(domain=domain, reachable=False, rank=rank[1:], url=url)
					final_results.append(ret)
					continue

				print("\n\n\t\t[RANK, URL, DOMAIN] = [%s, %s, %s]\n" % (rank, url, domain))

				# load all logs for that domain
				ret_dir = os.path.join(self._results_dir, domain)
				if os.path.exists(ret_dir) and os.path.isdir(ret_dir):
					files = os.listdir(ret_dir)

					ret = FinalResult(domain=domain, reachable=True, rank=rank, url=url)

					for ret_file in files:
						# parse that log
						parser = ParseLog(os.path.join(ret_dir, ret_file))
						# record the parser result
						ret.appendMaxLenFrameChain(parser.getMaxLengthOfFrameChain())
						ret.appendMaxLenCrossOriginFrameChain(parser.getMaxLengthOfCrossOriginFrameChain())
						ret.appendLargerLCrossOriginFrameChain(parser.getLargerCrossOriginFrameChain())
						ret.appendCrossOriginFrameChains(parser.getVulnCorssOriginFrames())
						ret.appendResultFileName(ret_file)

					ret.collectMetadata()
					final_results.append(ret)

			f.close()

		return final_results


def run():
	outputAtConsole()

	final_results = Parse().run()

	# log
	output = FinalResultList(final_results, logging)
	output.printRawDataTable()
	output.printDistributionTable()
	output.printCrossOriginDomains()
	output.printDistributionOfCrossOriginDomains()


if __name__ == '__main__':
	run()
