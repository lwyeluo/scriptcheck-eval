# coding=utf-8

'''
The Alexa top sites have some subdomains which set document.domain.
We need to do a further experiment on how these subdomains set document.domain.

The subdomains are saved in a json file in _target_subdomains_json_file
'''

from url_crawler.crawlImpl import CrawlerImpl
from document_domain import _urls_dir
from utils.globalDefinition import _target_subdomains_json_file
from document_domain.manualHomePage import _homepage_subdomains
from utils.executor import execute
import json
import threadpool


class CrawlSubDomainURL(object):
	def __init__(self):
		self.max_url_num = 50
		self.thread_num = 40

		self.urls_key = 'urls'

		# some ignore domains
		self.ignored_subdomains = [
			'staticxx.facebook.com',
			'www.facebook.com'
		]

		# mkdir
		execute("rm -rf %s || true" % _urls_dir)
		execute("mkdir %s || true" % _urls_dir)
		pass

	def crawl(self):
		task_args = []

		input_data = {}
		with open(_target_subdomains_json_file, 'r') as f:
			input_data = json.load(f)
		for domain in input_data.keys():
			if domain in self.ignored_subdomains:
				continue

			if self.urls_key not in input_data[domain].keys():
				continue

			urls = input_data[domain][self.urls_key]
			if len(urls) == 0:
				homepage = _homepage_subdomains[domain]
				if homepage is None:
					continue
				urls = [homepage]

			# the args for our crawler task
			arg = [domain, urls, _urls_dir, 1]
			task_args.append((arg, None))

		pool = threadpool.ThreadPool(self.thread_num)
		tasks = threadpool.makeRequests(CrawlerImpl(self.max_url_num).get_domain_url, task_args)
		for task in tasks:
			pool.putRequest(task)
		pool.wait()

def run():
	CrawlSubDomainURL().crawl()


if __name__ == '__main__':
	CrawlSubDomainURL().crawl()
