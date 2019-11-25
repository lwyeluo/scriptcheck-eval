import json

def test():
	fp = open("frame-structure-3", "w")
	with open("frame-structure-2", "r") as f:
		for line in f.readlines():
			if line.strip("\n").count('.') in [0, 1]:
				continue
			_, s, remain = line.strip("\n").partition("\t")
			if remain.count('.') == 0:
				continue
			fp.write(line)
	fp.close()

def getAllRanks():
	sites = {}
	with open("raw_domains", "r") as f:
		i = 1
		for line in f.readlines():
			site = line.strip("\n")
			sites[site] = i
			i = i + 1
	return sites

def testRank():
	fp = open("vulnerable_due_to_2mdn_net_with_rank", "w")

	sites = getAllRanks()

	vuln_site = {}
	with open("vulnerable_due_to_2mdn_net", "r") as f:
		for line in f.readlines():
			site = line.strip("\n")
			vuln_site[sites[site]] = site

	for k in sorted(vuln_site.keys()):
		print(k, vuln_site[k])

def testSetDomainRank():
	sites = getAllRanks()
	vuln_site = {}

	from utils.tld import getSite

	fp = open("suspected-domains", "w")
	with open("suspectedSubDomains", "r") as f:
		data = json.load(f)
		for k in data.keys():
			s = getSite(k)
			if s not in sites.keys():
				continue
			vuln_site[sites[s]] = {
				"site": s,
				"subdomain": k,
				"details": data[k]
			}
	for k in sorted(vuln_site.keys()):
		record = "%s\t%s\t%s\t" % (k, vuln_site[k]["site"], vuln_site[k]["subdomain"])
		print(record)
		# record += " ".join(vuln_site[k]["details"]["urls"])
		# record += "\n"
		# fp.write(record)
	json.dump(vuln_site, fp, indent=2)
	fp.close()

if __name__ == '__main__':
	testSetDomainRank()