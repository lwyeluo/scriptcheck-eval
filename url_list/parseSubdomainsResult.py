# coding=utf-8

'''
Parse the logs for subdomains
'''


import os
import re
import threadpool
from multiprocessing import Process, Manager
from url_list import _subdomains_dir


'''
Parse a log file to collect the information of Frames
'''
class ParseSubDomainLog(object):
	def __init__(self):
		self.filepath = None
		self.results = {}

		# features in log
		self.feature_new_frame = ">>> [Key] add a new principal. [cid, principal, url, frame_id] = "
		self.feature_set_domain = ">>> Document::setDomain. [old, new] = "

	'''
		Parse the principal: 5:3_https://blog.csdn.net/
			The format is [processId:routingId_origin]
	'''
	def matchPrincipal(self, principal):
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

	def handleNewFrame(self, log):
		line = log[log.index(self.feature_new_frame):]
		_, _, remain = line.partition("=")

		info = remain.split(", ")
		if len(info) != 4:
			raise Exception("Bad format: %s" % remain)

		# omit the chrome-search://
		if info[2] == '' or info[2].startswith("chrome-search://"):
			return

		frame_info = self.matchPrincipal(info[1])
		if not frame_info:
			raise Exception("Bad format when matching principal: %s" % remain)

		self.results[self.filepath]['frames'].append({
			'url': info[2].strip(' '),
			'process_id': frame_info['process_id'],
			'id': frame_info['id'],
			'origin': frame_info['origin']
		})

	def handleSetDomain(self, log):
		line = log[log.index(self.feature_set_domain):]
		_, _, remain = line.partition("=")

		info = remain.split(", ")
		if len(info) != 2:
			raise Exception("Bad format: %s" % remain)

		self.results[self.filepath]['setDomains'].append({
			'old': info[0],
			'new': info[1]
		})

	def run(self, filepath):
		self.filepath = filepath
		if not os.path.isfile(self.filepath):
			return None

		print(">>> HANDLER %s " % self.filepath)

		self.results[self.filepath] = {
			'frames': [],
			"setDomains": [],
		}

		with open(self.filepath, 'r', encoding="ISO-8859-1") as f:

			content = f.readlines()
			for line in content:
				log = line.strip('\n')

				if self.feature_new_frame in log:
					self.handleNewFrame(log)
				elif self.feature_set_domain in log:
					self.handleSetDomain(log)

			f.close()


'''
The entry class
'''
class ParseSubDomain(object):

	def __init__(self, domain=None, is_all=False):
		self.domain = domain
		self.is_all = is_all

		self.thread_num = 40

	def runDomain(self, domain, out_file_path):
		final_results = []

		try:
			dir = os.path.join(_subdomains_dir, domain)
			log_dir = os.path.join(dir, 'results')
			urls = os.listdir(log_dir)

			# create a thread pool
			task_pool = threadpool.ThreadPool(self.thread_num)
			request_list = []

			# add task
			tasks = []  # save the ParseSubDomainLog instance
			for url in urls:
				log_path = os.path.join(log_dir, url)

				# create a new ParseSubDomainLog instance
				p = ParseSubDomainLog()
				tasks.append(p)

				# add task into threadpool
				request_list += threadpool.makeRequests(p.run, [((log_path,), {})])

			# run the task
			[task_pool.putRequest(req) for req in request_list]
			# wait
			task_pool.wait()

			# read the results
			for p in tasks:
				final_results.append(p.results)

		except Exception as e:
			pass

		# record the results
		if not final_results:
			return

		vuln_results = []
		with open(out_file_path, 'w') as f:
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




		return

	def run(self):
		if self.is_all:
			# find all domains
			domains = os.listdir(_subdomains_dir)

			# collect the results for each process
			jobs = []

			# start process
			for domain in domains:
				# output_filepath
				output_dir = os.path.join(_subdomains_dir, domain)
				output_filepath = os.path.join(output_dir, "parsed-results")

				p = Process(target=self.runDomain, args=(domain, output_filepath))
				p.daemon = False
				jobs.append(p)
				p.start()

			# wait for the termination
			for job in jobs:
				job.join()

		elif self.domain:
			# output_filepath
			output_dir = os.path.join(_subdomains_dir, self.domain)
			output_filepath = os.path.join(output_dir, "parsed-results")

			self.runDomain(self.domain, output_filepath)


def run(domain, is_all=False):
	p = None
	if is_all:
		p = ParseSubDomain(domain=None, is_all=True)
	elif domain:
		p = ParseSubDomain(domain=domain, is_all=False)
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
