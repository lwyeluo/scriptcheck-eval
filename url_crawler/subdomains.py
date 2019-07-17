# coding=utf-8

import os
import requests
import threadpool
from url_crawler import _subdomains_dir


class CrawlerSubDomain(object):

	def __init__(self, domain):
		subdomain_dir = os.path.join(_subdomains_dir, domain)
		self.subdomain_file = os.path.join(subdomain_dir, "raw_subdomains")
		self.subdomain_reachable_file = os.path.join(subdomain_dir, "reachable_subdomains")

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

		self.homepage_list = []  # save the home pages' urls for these subdomains

	def isReachable(self, subdomain):
		for url in ["https://" + subdomain, "http://" + subdomain]:
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
			with open(self.subdomain_reachable_file, "w") as f:
				for homepage in self.homepage_list:
					f.write("%s\n" % homepage)
				f.close()


	def run(self):
		# get the url for subdomains' home pages
		if not os.path.exists(self.subdomain_file):
			raise Exception("%s does not exist" % self.subdomain_file)


		total_subdomains = 0

		# the thread pool
		task_pool = threadpool.ThreadPool(self.thread_num)
		request_list = []

		# read subdomains
		with open(self.subdomain_file, "r") as f:
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


def run(domain):
	CrawlerSubDomain(domain).run()
