# coding=utf-8

import os
from publicsuffix import PublicSuffixList

# _suffix_file_path = os.path.join(os.path.dirname(__file__), "public_suffix_list.dat")
psl = PublicSuffixList()

def isSitePlusTLD(domain):
	site = psl.get_public_suffix(domain)
	return site == domain

def getSite(domain):
	return psl.get_public_suffix(domain)

def levelOfDomain(domain):
	site = getSite(domain)
	domain = domain.replace(site, "")
	num = domain.count('.')
	return num + 2


def test():
	domains = [
		'yahoo.com', 'tmall.com', 'www.bbc.co.uk', 'zcwood.co.chinafloor.cn', 'appspot.com'
	]
	for domain in domains:
		print("%s->%s" % (domain, str(isSitePlusTLD(domain))))
		print("level is %d" % levelOfDomain(domain))

if __name__ == '__main__':
	test()