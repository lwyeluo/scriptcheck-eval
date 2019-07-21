import requests,time
from lxml import etree
import os
import queue
import threadpool

from utils.executor import execute
from utils.regMatch import matchDomainFromURL
from url_crawler import _subdomains_dir, _topsites_alexa_dir


class CrawlerImpl(object):

	def __init__(self, max_url_num):
		self.max_url_num = max_url_num

		self.headers = {
			'pragma': "no-cache",
			'accept-encoding': "gzip, deflate, br",
			'accept-language': "zh-CN,zh;q=0.8",
			'upgrade-insecure-requests': "1",
			'user-agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
			'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
			'cache-control': "no-cache",
			'connection': "keep-alive",
		}

	def requests_for_url(self, url, domain):
		return_set = set()

		try:
			response = requests.request("GET", url, headers=self.headers, timeout=10)
			selector = etree.HTML(response.text, parser=etree.HTMLParser(encoding='utf-8'))

			if response.status_code != 200:
				return return_set

		except Exception as e:
			# print("Fail to load URL", e)
			return return_set

		try:
			context = selector.xpath('//a/@href')
			for i in context:
				try:
					if i[0] == "j":
						continue
					if i[0] == "/":
						i = url + i.replace("/", "")
					return_set.add(i)
				except Exception as e:
					print("1", e, url)
		except Exception as e:
			print("2", e, url)

		result = set()
		for url in return_set:
			if domain not in url:
				continue
			url = url.strip().strip("\n")
			if len(url) == 0 or "http" not in url:
				continue
			result.add(url)

		return result

	def get_domain_url(self, domain, homepage, results_dir):
		urls = set()
		url_q = queue.Queue()

		# add the home page
		urls.add(homepage)
		url_q.put(homepage)

		# crawler
		while not url_q.empty() and len(urls) < self.max_url_num:
			url = url_q.get()
			return_set = self.requests_for_url(url, domain)
			print(url, len(urls), url_q.qsize(), len(return_set))
			for return_url in return_set:
				if return_url not in urls:
					urls.add(return_url)
					url_q.put(return_url)
				if len(urls) >= self.max_url_num:
					break

		output_filepath = os.path.join(results_dir, domain)
		with open(output_filepath, "w") as f:
			for url in urls:
				f.write(url + "\n")
			f.close()


class Crawler(object):

	'''
	@file_for_home_pages: the file saving the list for home pages
	@max_url_num
	'''
	def __init__(self, filepath_for_home_pages, max_url_num=100):
		self.input_file = filepath_for_home_pages
		self.max_url_num = max_url_num

		self.thread_num = 40

		# create the directory to save results
		self.result_dir = os.path.join(os.path.dirname(self.input_file), 'urls')
		if os.path.exists(self.result_dir):
			execute("rm -rf %s || true" % self.result_dir)
		execute("mkdir %s || true" % self.result_dir)

	def run(self):

		task_args = []

		# read url and domain from input_file
		with open(self.input_file, 'r') as f:
			content = f.readlines()
			for line in content:
				url = line.strip('\n') + '/'
				domain = matchDomainFromURL(url)
				if not domain:
					raise Exception("Bad Domain. url is %s" % url)

				# the args for our crawler task
				arg = [domain, url, self.result_dir]
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
	max_url_num = 50
	if type == 'SubDomain':
		if not domain:
			raise Exception("The DOMAIN for SubDomain should not be None")

		filedir = os.path.join(_subdomains_dir, domain)
		if not os.path.exists(filedir):
			raise Exception("Filepath does not exist. %s", filedir)

		filepath = os.path.join(filedir, "reachable_subdomains")

	elif type == 'Alexa':
		filepath = os.path.join(_topsites_alexa_dir, "reachable_domains")
		max_url_num = 10

	elif type == 'China':
		raise Exception("TO DO it later")

	if not os.path.exists(filepath):
		raise Exception("Filepath does not exist. %s", filepath)

	# run
	crawler = Crawler(filepath, max_url_num)
	crawler.run()














