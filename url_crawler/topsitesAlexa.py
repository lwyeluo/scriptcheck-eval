# coding=utf-8

import os
import requests
import threadpool
from url_crawler import _topsites_alexa_dir


class CrawlerTopSites(object):

	def __init__(self):
		self.domain_file = os.path.join(_topsites_alexa_dir, "raw_domains")
		self.domain_reachable_file = os.path.join(_topsites_alexa_dir, "reachable_domains")

		self.http_headers = {
			'pragma': "no-cache",
			'accept-encoding': "gzip, deflate, br",
			'accept-language': "zh-CN,zh;q=0.8",
			'upgrade-insecure-requests': "1",
			'user-agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
			'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
			'cache-control': "no-cache",
			'connection': "keep-alive",
		}

		self.thread_num = 40

		self.homepage_list = []  # save the home pages' urls for these domains

	def isReachable(self, domain):
		for url in ["https://www." + domain, "http://www." + domain,
					"https://" + domain, "http://" + domain]:
			try:
				response = requests.request("GET", url, headers=self.http_headers, timeout=10)
				print(">>> try %s: the status code is %d" % (url, response.status_code))
				if response.status_code == 200:
					return url
			except Exception as e:
				print("Failed to load %s" % url, e)
		return None

	def getHomepage(self, request, result):
		# the subdomain is request.args[0]
		# record the url
		if result:
			self.homepage_list.append(result)

	def writeHomePagesToFile(self):
		# save urls into self.subdomain_reachable_file
		if self.homepage_list:
			with open(self.domain_reachable_file, "w") as f:
				for homepage in self.homepage_list:
					f.write("%s\n" % homepage)
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
				domain = line.strip("\n")

				# test the domain is reachable using thread pool
				request_list += threadpool.makeRequests(
					self.isReachable, [((domain, ), {})], callback=self.getHomepage)

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
