# coding=utf-8

import re


def matchDomainFromURL(url):
	reg = "(http|https):\/\/(www.)?([^\/]+)\/?"
	m = re.match(reg, url)
	if m:
		# print(m.group(0), m.group(1), m.group(2), m.group(3))
		return m.group(3)
	return None

if __name__ == '__main__':
	url = "http://www.chewen.com/"
	domain = matchDomainFromURL(url)
	print(domain)