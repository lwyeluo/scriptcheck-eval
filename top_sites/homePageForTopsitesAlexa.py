# coding=utf-8

import os
import requests
import threadpool
from utils.globalDefinition import _topsites_dir, _USE_PROXY_
from utils.executor import execute


class CrawlerTopSites(object):

	def __init__(self):
		self.domain_file = os.path.join(_topsites_dir, "raw_domains")
		self.domain_reachable_file = os.path.join(_topsites_dir, "reachable_domains")

		self.thread_num = 40

		self.homepage_list = {}  # save the home pages' urls for these domains

	def isReachable(self, domain, rank):
		print(">>>> HANDLE %s" % domain)
		for url in ["https://www." + domain, "http://www." + domain,
					"https://" + domain, "http://" + domain]:
			try:
				cmd = ""
				if _USE_PROXY_:
					cmd = 'proxychains4 wget "%s" --tries=3 -O test.html' % url
				else:
					cmd = 'wget "%s" --tries=3 -O test.html' % url
				output = execute(cmd)
				print(">>> try %s..." % url)
				return url, rank
			except Exception as e:
				print("Failed to load %s" % url, e)
		return None, None

	def getHomepage(self, request, result):
		# the subdomain is request.args[0]
		# record the url
		print(result)
		url, rank = result[0], result[1]
		if url and rank:
			self.homepage_list[int(rank)] = url

	def writeHomePagesToFile(self):
		# save urls into self.subdomain_reachable_file
		if self.homepage_list:
			with open(self.domain_reachable_file, "w") as f:
				for rank in sorted(self.homepage_list.keys()):
					f.write("%s\t%s\n" % (rank, self.homepage_list[rank]))
				f.close()


	def run(self):
		# get the url for domains' home pages
		if not os.path.exists(self.domain_file):
			raise Exception("%s does not exist" % self.domain_file)

		total_subdomains = 0

		# the thread pool
		task_pool = threadpool.ThreadPool(self.thread_num)
		request_list = []

		# read subdomains
		with open(self.domain_file, "r") as f:
			content = f.readlines()
			total_subdomains = len(content)
			for line in content:
				if line.find("#") == 0:
					continue
				data = line.strip("\n").split("\t")
				print(data)
				if len(data) != 2:
					continue

				rank, domain = data[0], data[1]

				# test the domain is reachable using thread pool
				request_list += threadpool.makeRequests(
					self.isReachable, [((domain, rank, ), {})], callback=self.getHomepage)

			f.close()

		# run the task
		[task_pool.putRequest(req) for req in request_list]
		# wait
		task_pool.wait()

		# write homepages into file
		self.writeHomePagesToFile()

		print("RESULTS: subdomains: reachable/all=%d/%d=%f%%" % (len(self.homepage_list), total_subdomains,
																 len(self.homepage_list)/total_subdomains*100))


def run():
	CrawlerTopSites().run()
