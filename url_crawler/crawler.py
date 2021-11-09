# coding=utf-8


import os
import threadpool

from utils.executor import execute
from utils.regMatch import matchDomainFromURL
from utils.globalDefinition import _subdomains_dir, _topsites_dir
from url_crawler.crawlImpl import CrawlerImpl


class Crawler(object):

	'''
	@file_for_home_pages: the file saving the list for home pages
	@max_url_num
	'''
	def __init__(self, filepath_for_home_pages, max_url_num=100):
		self.input_file = filepath_for_home_pages
		self.max_url_num = max_url_num

		self.thread_num = 100

		# create the directory to save results
		self.result_dir = os.path.join(os.path.dirname(self.input_file), 'urls')
		self.store_html_dir = os.path.join(os.path.dirname(self.input_file), 'htmls')
		if os.path.exists(self.result_dir):
			execute("rm -rf %s || true" % self.result_dir)
		execute("mkdir %s || true" % self.result_dir)

		if os.path.exists(self.store_html_dir):
			execute("rm -rf %s || true" % self.store_html_dir)
		execute("mkdir %s || true" % self.store_html_dir)

	def run(self):

		task_args = []

		# read url and domain from input_file
		with open(self.input_file, 'r') as f:
			content = f.readlines()
			for line in content:
				data = line.strip('\n').split("\t")
				if len(data) != 2:
					raise Exception("Bad input data: %s" % line)
				url = data[1] + '/'
				domain = matchDomainFromURL(url)
				if not domain:
					raise Exception("Bad Domain. url is %s" % url)

				# the args for our crawler task
				arg = [domain, url, self.result_dir, self.store_html_dir]
				task_args.append((arg, None))

			f.close()

		pool = threadpool.ThreadPool(self.thread_num)
		tasks = threadpool.makeRequests(CrawlerImpl(self.max_url_num).get_domain_url, task_args)
		for task in tasks:
			pool.putRequest(task)
		pool.wait()


'''
	@domain
	@type: SubDomain | Alexa | China
'''
def run(domain, type):
	filepath = None
	max_url_num = 10
	if type == 'SubDomain':
		if not domain:
			raise Exception("The DOMAIN for SubDomain should not be None")

		filedir = os.path.join(_subdomains_dir, domain)
		if not os.path.exists(filedir):
			raise Exception("Filepath does not exist. %s", filedir)

		filepath = os.path.join(filedir, "reachable_subdomains")

	elif type == 'Alexa':
		filepath = os.path.join(_topsites_dir, "reachable_domains")
		max_url_num = 5

	elif type == 'China':
		raise Exception("TO DO it later")

	if not os.path.exists(filepath):
		raise Exception("Filepath does not exist. %s", filepath)

	# run
	crawler = Crawler(filepath, max_url_num)
	crawler.run()














