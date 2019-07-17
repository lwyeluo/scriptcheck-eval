# coding=utf-8

import os
from subdomain_tracker import sublist3r
from url_list import _subdomains_dir
from utils.executor import execute


class FindSubDomain(object):

	def __init__(self, domain):
		self.domain = domain

		# get the filename
		filepath = os.path.join(_subdomains_dir, domain)
		if not os.path.exists(filepath):
			execute("mkdir -p %s" % filepath)

		self.output_filename = os.path.join(filepath, "raw_subdomains")

		self.threads = 40
		self.ports = None
		self.verbose = True
		self.enable_bruteforce = True

	def run(self):
		print(">>> parse the sub-domains for %s" % self.domain)
		subdomains = sublist3r.main(self.domain, self.threads,
									self.output_filename, self.ports, silent=False,
									verbose=self.verbose,
									enable_bruteforce=self.enable_bruteforce, engines=None)
		print(">>> done!")


def run(domain):
	FindSubDomain(domain).run()

if __name__ == '__main__':
	domain = "blog.csdn.net"
	FindSubDomain(domain).run()