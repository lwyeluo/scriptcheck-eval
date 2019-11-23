def test():
	fp = open("frame-structure-3", "w")
	with open("frame-structure-2", "r") as f:
		for line in f.readlines():
			if line.strip("\n").count('.') in [0, 1]:
				continue
			fp.write(line)
	fp.close()

def testRank():
	fp = open("vulnerable_due_to_2mdn_net_with_rank", "w")

	sites = {}
	with open("raw_domains", "r") as f:
		i = 1
		for line in f.readlines():
			site = line.strip("\n")
			sites[site] = i
			i = i + 1

	vuln_site = {}
	with open("vulnerable_due_to_2mdn_net", "r") as f:
		for line in f.readlines():
			site = line.strip("\n")
			vuln_site[sites[site]] = site

	for k in sorted(vuln_site.keys()):
		print(k, vuln_site[k])


if __name__ == '__main__':
	testRank()