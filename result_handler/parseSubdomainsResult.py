# coding=utf-8

'''
Parse the logs for subdomains
	For each log, we only record the frames and the events for setting document.domain
'''


import os
from result_handler.parseSubDomainLog import ParseSubDomainLog
from result_handler import _subdomains_dir


'''
The entry class
'''
class ParseSubDomain(object):

	def __init__(self, domain=None):
		self.domain = domain

		self.thread_num = 40

	def runSubDomain(self, subdomain, input_dir, out_file_path):
		final_results = []

		try:
			urls = os.listdir(input_dir)

			for url in urls:
				log_path = os.path.join(input_dir, url)

				# create a new ParseSubDomainLog instance
				p = ParseSubDomainLog()

				# parse the log
				p.run(log_path)

				# append the results
				final_results.append(p.results)

		except Exception as e:
			pass

		# record the results
		if not final_results:
			return

		vuln_results = []
		with open(out_file_path, 'a') as f:
			f.write("\n#####################################################\n")
			f.write("\t\tSubDomain: %s\n" % subdomain)
			f.write("#####################################################\n\n")
			for result in final_results:
				for path, data in result.items():
					f.write(">>> Handler %s\n" % path)
					f.write(str(data))
					f.write("\n")

					if len(data['setDomains']) > 0:
						vuln_results.append({
							path: data['setDomains']
						})
						f.write("\n\t\tPAY ATTENTION TO THIS\n")
					f.write("\n")

			if vuln_results:
				f.write("\n\n\n*******************************************\n")
				f.write("          We Set Domain!!!      \n")
				f.write("*******************************************\n")

			for vuln in vuln_results:
				print(vuln)
				f.write(str(vuln))
				f.write('\n')

			f.close()

		return vuln_results

	def run(self):
		# find all subdomains
		domain_dir = os.path.join(_subdomains_dir, self.domain)
		if not os.path.exists(domain_dir):
			raise Exception("Wrong domain. %s does not exist" % domain_dir)
		log_dir = os.path.join(domain_dir, 'results')
		subdomains = os.listdir(log_dir)

		# output_filepath
		output_dir = os.path.join(_subdomains_dir, self.domain)
		output_filepath = os.path.join(output_dir, "parsed-results")

		# clear the output_file
		with open(output_filepath, 'w') as f:
			f.write('')
			f.close()

		# start parser
		vuln_results = []
		for subdomain in subdomains:
			input_dir = os.path.join(log_dir, subdomain)
			vuln_result = self.runSubDomain(subdomain, input_dir, output_filepath)
			if vuln_result:
				vuln_results.append({subdomain: vuln_result})

		if len(vuln_results) > 0:
			print("\n\n***************************************************************")
			print("\t\t I found some web page setting domain!!!")
			print("***************************************************************")
			for vuln in vuln_results:
				print(vuln)


def run(domain):
	p = ParseSubDomain(domain=domain)
	p.run()


def test(filePath=None):
	if not filePath:
		filePath = '/Users/lwyeluo/Workspaces/lab-project/browser/tim-evaluate/' \
				   'url_list/subdomains/blog.csdn.net/results/https:,,009264.blog.csdn.net6KfNXI1Yvm'
	p = ParseSubDomainLog()
	p.run(filePath)
	print(p.results)


if __name__ == '__main__':
	test()
