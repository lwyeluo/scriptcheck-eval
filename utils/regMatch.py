# coding=utf-8

import re


def matchDomainFromURL(url):
	reg = "(http|https):\/\/(www.)?([^\/]+)\/?"
	m = re.match(reg, url)
	if m:
		# print(m.group(0), m.group(1), m.group(2), m.group(3))
		return m.group(3)
	return None

def matchRawDomainFromURL(url):
	reg = "(http|https):\/\/([^\/]+)\/?"
	m = re.match(reg, url)
	if m:
		# print(m.group(0), m.group(1), m.group(2))
		return m.group(2)
	return None

def getSiteFromURL(url):
	domain = matchRawDomainFromURL(url)
	if domain is None:
		return None
	from utils.tld import getSite
	return getSite(domain)

'''
	Parse the principal: 5:3_https://blog.csdn.net/
		The format is [processId:routingId_origin]
'''
def matchPrincipal(principal):
	reg = "(\d{1,}):(\d{1,})_([^\s/]+://[^\s/]+/)(.*)"
	m = re.match(reg, principal)
	if m:
		process_id, routing_id, origin, remain = m.group(1), m.group(2), m.group(3), m.group(4)
		return {
			'process_id': process_id,
			'id': routing_id,
			'origin': origin
		}
	return None

def strip_into_csv(s):
	return '"%s"' % s.replace('"', '""')

if __name__ == '__main__':
	url = "http://www.chewen.com/"
	domain = matchDomainFromURL(url)
	print(domain)