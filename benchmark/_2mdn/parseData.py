# coding=utf-8

'''
Parse the logs for subdomains
	For each log, we only record the frames and the events for setting document.domain
'''


import os
from result_handler.parseSubDomainLog import ParseSubDomainLog
from result_handler import _subdomains_dir


'''
The entry class
'''
class ParseResults(object):

	def __init__(self):
		self.thread_num = 40

		base_dir = os.path.dirname(os.path.abspath(__file__))
		self.results_dir = os.path.join(base_dir, "results")

	def runSite(self, site, input_dir):
		final_results = []

		try:
			urls = os.listdir(input_dir)

			for url in urls:
				log_path = os.path.join(input_dir, url)

				# create a new ParseSubDomainLog instance
				p = ParseSubDomainLog()

				# parse the log
				p.run(log_path)

				# append the results
				final_results.append(p.results)

		except Exception as e:
			pass

		# record the results
		if not final_results:
			return

		vuln_results = []
		for result in final_results:
			for path, data in result.items():
				flag = False
				for f in data["frames"]:
					if "2mdn" in f["url"]:
						flag = True
						break
				if flag:
					vuln_results.append({path: data})

		return vuln_results

	def run(self):
		# find all sites
		sites = os.listdir(self.results_dir)

		# start parser
		vuln_results = {}
		for site in sites:
			input_dir = os.path.join(self.results_dir, site)
			vuln_result = self.runSite(site, input_dir)
			if vuln_result:
				vuln_results[site] = vuln_result
		for site, data in vuln_results.items():
			print("\n\n>>>>> ", site)
			# print(data)
			for d in data:
				for path, info in d.items():
					for frame in info["frames"]:
						if frame["id"] == "3":
							print(frame["url"])
							break


def parse():
	p = ParseResults()
	p.run()

