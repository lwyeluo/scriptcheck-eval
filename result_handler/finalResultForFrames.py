# coding=utf-8

import json
from utils.regMatch import matchRawDomainFromURL
from utils.tld import isSitePlusTLD
from utils.logger import _logger
from result_handler import _topsites_output_domain_dir

class FinalResultForFrames(object):

	'''
		@domain
		@url
		@filepath
		@data: {'frames': [], 'setDomains': [{'old': old, 'new': new}]}
	'''
	def __init__(self, domain, url, filepath, data):
		self.domain = domain
		self.url = url
		self.filepath = filepath
		self.data = data

		# key
		self.set_domain_key = 'setDomains'
		self.frames_key = 'frames'

		self.old_domain_key = 'old'
		self.new_domain_key = 'new'

		self.frames_origin_key = 'origin'
		self.frames_url_key = 'url'

	'''
		get all events for setting domains
	'''
	def getSetDomains(self):
		set_domains = {}  # {old_domain: {new_domain: number}}
		if self.set_domain_key in self.data.keys():
			d = self.data[self.set_domain_key]
			if len(d) > 0:
				for set_domain in d:
					old, new = set_domain[self.old_domain_key], set_domain[self.new_domain_key]
					old = old.strip(' ').strip('"')
					new = new.strip(' ').strip('"')
					if old in set_domains.keys():
						if new in set_domains[old].keys():
							set_domains[old][new] += 1
						else:
							set_domains[old][new] = 1
					else:
						set_domains[old] = {new: 1}

		return set_domains

	'''
		get all events for subdomains setting their document.domain
	'''
	def getRestrictedSetDomains(self):
		set_domains = self.getSetDomains()
		sites = set()
		for key in set_domains.keys():
			if isSitePlusTLD(key):
				sites.add(key)
		for site in sites:
			set_domains.pop(site)
		return set_domains

	'''
		get all involved domains
	'''
	def getAllInvolvedDomainsAndURLs(self):
		all_domain_urls = {}  # {domain: set(urls)}
		if self.frames_key in self.data.keys():
			for frame in self.data[self.frames_key]:
				if self.frames_origin_key in frame.keys():
					origin = frame[self.frames_origin_key]
					domain = matchRawDomainFromURL(origin)
					if domain:
						if domain in all_domain_urls.keys():
							all_domain_urls[domain].add(frame[self.frames_url_key])
						else:
							s = set()
							s.add(frame[self.frames_url_key])
							all_domain_urls = {domain: s}
		return all_domain_urls

	'''
		get all involved sub-domains
	'''
	def getRestrictedInvolvedDomainsAndURLs(self):
		all_domain_urls = self.getAllInvolvedDomainsAndURLs() # {domain: set(urls)}
		sites = set()
		for domain in all_domain_urls.keys():
			if isSitePlusTLD(domain):
				sites.add(domain)
		for site in sites:
			all_domain_urls.pop(site)
		return all_domain_urls

class FinalResultListForFrames(object):

	'''
		@results: a list of FinalResultForFrames
	'''
	def __init__(self, results):
		self._results = results

		# for setting domains
		self._normal_key = 'normal'
		self._restricted_key = 'restricted'

		# just record all set_domains. {'normal': {old_domain: {new_domain: number}}, 'restricted': ...}
		self._raw_set_domains = {
			self._normal_key: {},
			self._restricted_key: {}
		}
		# the domain who set document.domain to its superdomain
		self._domains_set_as_super = {
			self._normal_key: [],
			self._restricted_key: []
		}
		# the domain who set document.domain to itself
		self._domains_set_as_itself = {
			self._normal_key: [],
			self._restricted_key: []
		}
		self._domains_set_as_both = {
			self._normal_key: [],
			self._restricted_key: []
		}
		# the domain who set document.domain to its-child!!!
		self._domains_set_as_child = {
			self._normal_key: [],
			self._restricted_key: []
		}

		# urls for each domain
		self._domains_involved = {
			self._normal_key: {},  # {domain: [urls]}
			self._restricted_key: {}
		}

		# urls for each domain which sets document.domain
		self._domains_urls_set_domains = {
			self._normal_key: {},  # {domain: {'setDomain': [{new: num}], 'urls': [urls]}}
			self._restricted_key: {}
		}

		self._log = _logger

		self.compute()

	def computeDomains(self, type):
		# 1. merge all setDomains
		for result in self._results:
			if not isinstance(result, FinalResultForFrames):
				raise Exception("Bad format")

			# get the data
			set_domains = {}
			if type == self._normal_key:
				set_domains = result.getSetDomains()
			elif type == self._restricted_key:
				set_domains = result.getRestrictedSetDomains()
			else:
				return

			# merge into self._raw_set_domains
			for old, v in set_domains.items():
				if old not in self._raw_set_domains[type].keys():
					self._raw_set_domains[type][old] = v
				else:
					# self._raw_set_domains has old, so we need to merge
					for new, num in v.items():
						if new in self._raw_set_domains[type][old].keys():
							self._raw_set_domains[type][old][new] += num
						else:
							self._raw_set_domains[type][old][new] = num

		# 2. maintain a domain has raised to its superdomain/itself/both
		for old, v in self._raw_set_domains[type].items():
			is_both = -2
			for new, num in v.items():
				if old == new:
					self._domains_set_as_itself[type].append(old)
					is_both += 1
				elif old.find(new) > 0:
					self._domains_set_as_super[type].append(old)
					is_both += 1
				else:
					self._domains_set_as_child[type].append(old)
					#raise Exception("Domain set document.domain to its child. %s->%s" % (old, new))

			if is_both == 0:
				self._domains_set_as_both[type].append(old)

		# 3. get all involved domains
		for result in self._results:
			domains = {}
			if type == self._normal_key:
				domains = result.getAllInvolvedDomainsAndURLs()
			elif type == self._restricted_key:
				domains = result.getRestrictedInvolvedDomainsAndURLs()
			else:
				return
			for domain, urls in domains.items():
				if domain not in self._domains_involved[type].keys():
					self._domains_involved[type][domain] = urls
				else:
					for url in urls:
						self._domains_involved[type][domain].add(url)

		# transfer set to list
		for domain, urls in self._domains_involved[type].items():
			if isinstance(urls, set):
				self._domains_involved[type][domain] = list(urls)

		# 4. compute self._domains_urls_set_domains
		for domain in self._raw_set_domains[type].keys():
			if domain not in self._domains_involved[type].keys():
				self._domains_urls_set_domains[type][domain] = {
					'setDomain': self._raw_set_domains[type][domain],
					'urls': []
				}
			else:
				self._domains_urls_set_domains[type][domain] = {
					'setDomain': self._raw_set_domains[type][domain],
					'urls': self._domains_involved[type][domain]
				}


	def compute(self):
		self.computeDomains(self._normal_key)
		self.computeDomains(self._restricted_key)

	def printInformationForSettingDomains(self, type):
		self._log.info("\n\n")
		self._log.info("#######################################")
		self._log.info("# Information for setting domains [%s] #" % type)
		self._log.info("#######################################")

		self._log.info("\nold_domain\tsetAsSuper\tsetAsItself\tsetAsSuperAndItself\tsetAsChild\tnew_domains\n")
		for old in self._raw_set_domains[type].keys():
			s = old

			if old in self._domains_set_as_super[type]:
				s += '\tY'
			else:
				s += '\tN'

			if old in self._domains_set_as_itself[type]:
				s += '\tY'
			else:
				s += '\tN'

			if old in self._domains_set_as_both[type]:
				s += '\tY'
			else:
				s += '\tN'

			if old in self._domains_set_as_child[type]:
				s += '\tY'
			else:
				s += '\tN'

			s += '\t' + ','.join(self._raw_set_domains[type][old].keys())

			self._log.info(s)

	def printSummaryForDomains(self, type):
		self._log.info("\n\n")
		self._log.info("#######################################")
		self._log.info("# Summary for setting domains [%s] #" % type)
		self._log.info("#######################################")

		s = "\n#domainsInvolved = %d, #domains = %d, #domainsSetAsSuper = %d, #domainsSetAsItself = %d, #domainsSetAsSuperAndItself = %d," \
			"#domainsSetAsChild = %d" % (
			len(self._domains_involved[type]),
			len(self._raw_set_domains[type].keys()), len(self._domains_set_as_super[type]),
			len(self._domains_set_as_itself[type]), len(self._domains_set_as_both[type]),
			len(self._domains_set_as_child[type])
		)
		self._log.info(s)

	def printNormal(self):
		self.printInformationForSettingDomains(self._normal_key)
		self.printSummaryForDomains(self._normal_key)

		self._log.info(json.dumps(self._raw_set_domains[self._normal_key], indent=2))

	def print(self):
		self.printSummaryForDomains(self._normal_key)
		self.printSummaryForDomains(self._restricted_key)

		# with open(_topsites_output_domain_dir, 'w') as f:
		# 	json.dump(self._raw_set_domains[self._restricted_key], f, indent=2)
		# 	f.close()

		with open(_topsites_output_domain_dir, 'w') as f:
			# f.write("\n\n\n\n\n\n")
			json.dump(self._domains_urls_set_domains[self._restricted_key], f, indent=2)
			f.close()





