# coding=utf-8

import os
from url_crawler import _subdomains_dir


class CrawlerSubDomain(object):

	def __init__(self, domain):
		subdomain_dir = os.path.join(_subdomains_dir, domain)
		self.subdomain_file = os.path.join(subdomain_dir, "raw_subdomains")

		# get the url for subdomains' home pages
		self.url_list = self.run()

	def run(self):
		if not os.path.exists(self.subdomain_file):
			raise Exception("%s does not exist" % self.subdomain_file)

		subdomain_list = []

		with open(self.subdomain_file, "r") as f:
			content = f.readlines()
			for line in content:
				domain = line.strip("\n")
				subdomain_list.append(domain)

			f.close()

		return subdomain_list


def run(domain):
	print(CrawlerSubDomain(domain).url_list)
