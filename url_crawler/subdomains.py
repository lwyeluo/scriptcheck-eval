# coding=utf-8

import os
import requests
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

	def isReachable(self, subdomain):
		for url in ["https://" + subdomain, "http://" + subdomain]:
			try:
				print(">>> try %s" % url)
				response = requests.request("GET", url, headers=self.http_headers, timeout=10)
				print("\tthe status code is %d" % response.status_code)
				if response.status_code == 200:
					return url
			except Exception as e:
				print("Failed to load %s" % url, e)
		return None


	def run(self):
		# get the url for subdomains' home pages
		if not os.path.exists(self.subdomain_file):
			raise Exception("%s does not exist" % self.subdomain_file)

		homepage_list = []  # save the home pages' urls for these subdomains
		total_subdomains = 0

		with open(self.subdomain_file, "r") as f:
			content = f.readlines()
			total_subdomains = len(content)
			for line in content:
				domain = line.strip("\n")

				# test the domain is reachable
				url = self.isReachable(domain)
				if url:
					homepage_list.append(url)

			f.close()

		# save urls into self.subdomain_reachable_file
		if homepage_list:
			with open(self.subdomain_reachable_file, "w") as f:
				for homepage in homepage_list:
					f.write("%s\n" % homepage)
				f.close()

		print("RESULTS: subdomains: reachable/all=%d/%d=%f%%" % (len(homepage_list), total_subdomains,
																 len(homepage_list)/total_subdomains*100))


def run(domain):
	CrawlerSubDomain(domain).run()
