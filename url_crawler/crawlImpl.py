# coding=utf-8

import queue
import os
import requests,time
from lxml import etree
from utils.regMatch import matchRawDomainFromURL

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

	'''
		@rule:
			0: the crawled url must contains @domain, means that the url may be a subdomain
			1: the crawled url must have the same domain with @domain
	'''
	def requests_for_url(self, url, domain, rule=0):
		return_set = set()

		try:
			response = requests.request("GET", url, headers=self.headers, timeout=10, allow_redirects=False)
			selector = etree.HTML(response.text, parser=etree.HTMLParser(encoding='utf-8'))

			if response.status_code != 200:
				return None

		except Exception as e:
			# print("Fail to load URL", e)
			return None

		try:
			context = selector.xpath('//a/@href')
			for i in context:
				try:
					if i[0] == "j":
						continue
					if i.find('//') == 0:
						u = i[2:]
						return_set.add('https://' + u)
						return_set.add('http://' + u)
						continue
					elif i[0] == "/":
						i = url + i.replace("/", "")
					return_set.add(i)
				except Exception as e:
					print("1", e, url)
		except Exception as e:
			print("2", e, url)

		result = set()
		for url in return_set:
			if rule == 0 and domain not in url:
				continue
			if rule == 1:
				d = matchRawDomainFromURL(url)
				if d is None or d != domain:
					continue
			url = url.strip().strip("\n")
			if len(url) == 0 or "http" not in url:
				continue
			result.add(url)

		return result

	'''
		@rule:
			0: the crawled url must contains @domain, means that the url may be a subdomain
			1: the crawled url must have the same domain with @domain
	'''
	def get_domain_url(self, domain, homepage, results_dir, rule=0):
		print(">>> TRY [domain, url] = ", domain, homepage)
		urls = set()
		url_q = queue.Queue()

		# add the home page
		if isinstance(homepage, list):
			for h in homepage:
				# urls.add(h)
				url_q.put(h)
		elif isinstance(homepage, str):
			urls.add(homepage)
			url_q.put(homepage)

		# crawler
		while not url_q.empty() and len(urls) < self.max_url_num:
			url = url_q.get()
			return_set = self.requests_for_url(url, domain, rule)
			if return_set is None:
				continue
			else:
				urls.add(url)

			print(url, len(urls), url_q.qsize(), len(return_set))
			for return_url in return_set:
				if return_url not in urls:
					#urls.add(return_url)
					url_q.put(return_url)
				if len(urls) >= self.max_url_num:
					break

		output_filepath = os.path.join(results_dir, domain)
		with open(output_filepath, "w") as f:
			for url in urls:
				f.write(url + "\n")
			f.close()

	def test(self):
		url = 'https://sinoptik.ua'
		domain = matchRawDomainFromURL(url)
		print(self.requests_for_url(url, domain))

if __name__ == '__main__':
	CrawlerImpl(100).test()
