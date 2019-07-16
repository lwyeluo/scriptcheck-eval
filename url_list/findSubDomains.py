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
		self.ports = "80,443"
		self.verbose = True
		self.enable_bruteforce = False

	def run(self):
		print(">>> parse the sub-domains for %s" % self.domain)
		subdomains = sublist3r.main(self.domain, self.threads,
									None, self.ports, silent=False,
									verbose=self.verbose,
									enable_bruteforce=self.enable_bruteforce, engines=None)

		print(">>> record the results")
		with open(self.output_filename, 'w') as f:
			if self.ports and type(subdomains) is dict:
				for subdomain, ports in subdomains.items():
					f.write("%s\t%s\n" % (subdomain, ','.join(ports)))

			f.close()
		print(">>> done!")


def run(domain):
	FindSubDomain(domain).run()

if __name__ == '__main__':
	domain = "blog.csdn.net"
	FindSubDomain(domain).run()