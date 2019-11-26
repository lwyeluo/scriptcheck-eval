# coding=utf-8

import os
import json
import subprocess
import logging
import os
import multiprocessing

import codecs

_logger = logging.getLogger('')

_dir = os.path.abspath(os.path.dirname(__file__))
_log_filename = os.path.join(_dir, "result-attack.log")

print(">>> log file is " + _log_filename)

def outputAtConsole():
	_logger.setLevel(logging.DEBUG)

	# console handler
	console = logging.StreamHandler()
	console.setFormatter(logging.Formatter("%(message)s"))
	console.setLevel(logging.DEBUG)

	# log handler
	with open(_log_filename, 'w') as f:
		f.write("")
		f.close()
	log_file = logging.FileHandler(_log_filename)
	log_file.setFormatter(logging.Formatter("%(message)s"))
	log_file.setLevel(logging.DEBUG)

	_logger.addHandler(log_file)
	_logger.addHandler(console)

outputAtConsole()

def executeWithoutCheckStatus(cmd):
	(status, output) = subprocess.getstatusoutput(cmd)
	return output

class Parse(object):

	def __init__(self, min_rank = 0, max_rank = 20000):
		_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		_tim_evaluate_dir = os.path.dirname(_dir)
		_xsstrike_dir = os.path.join(os.path.dirname(_tim_evaluate_dir), "XSStrike")
		self._cmd_path = os.path.join(_xsstrike_dir, "xsstrike.py")
		print(self._cmd_path)

		self._domain_path = "suspected-domains"
		fp = open(self._domain_path, "r")
		self._domain_data = json.load(fp)
		fp.close()

		# output
		self._output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vuln_subdomains")
		self._output_path = os.path.join(self._output_dir, "subdomains_with_vector")

		self._min_rank = min_rank
		self._max_rank = max_rank
		self._thread_num = 8

		# indicators for xsstrike
		self._xsstrike_vuln = "Vulnerable webpage: "
		self._xsstrike_vector = "Vector for "

		self.final_urls = {}

	def runForVector(self):

		# # the thread pool
		# task_pool = threadpool.ThreadPool(self._thread_num)
		# request_list = []

		# the process pool
		pool = multiprocessing.Pool(self._thread_num)
		results = []

		for k in sorted(self._domain_data.keys()):
			rank = int(k)
			if rank < self._min_rank or rank > self._max_rank:
				continue
			site = self._domain_data[k]["site"]
			domain = self._domain_data[k]["subdomain"]
			urls = self._domain_data[k]["details"]["urls"]
			if domain == "staticxx.facebook.com":
				continue
			if len(urls) == 0:
				continue

			_logger.info("\n\n<--- Handler [rank, domain] = [%d, %s]\n" % (rank, domain))

			for url in urls:
				_logger.info("\t URL is " + url)

				# request_list += threadpool.makeRequests(
				# 	self.handleUrl, [((url, rank), {})], callback=self.threadCallback)
				results.append(pool.apply_async(self.handleUrl, (url, rank, )))

		# # run the task
		# [task_pool.putRequest(req) for req in request_list]
		# # wait
		# task_pool.wait()

		pool.close()
		pool.join()
		for ret in results:
			self.final_urls.update(ret.get())

		# write homepages into file
		self.writeToFile()


	def handleUrl(self, url, rank):
		print(" ".join(["python3", self._cmd_path, "-u", url, "--crawl"]))
		process_node = subprocess.Popen(["python3", self._cmd_path, "-u", url, "--crawl"],
										shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		vuln_pages = []
		vuln_vectors = []
		while process_node.poll() is None:
			line = process_node.stdout.readline()
			line = line.strip().decode("utf-8")
			if line:
				print('Subprogram output: [{}]'.format(line))
				if self._xsstrike_vuln in line:
					_, _, v = line.partition(self._xsstrike_vuln)
					v = v.strip("'").replace(" ", "")
					print(">>> Find a vulnerable page: " + v)
					vuln_pages.append(v)
				elif self._xsstrike_vector in line:
					_, _, v = line.partition(self._xsstrike_vector)
					vec, _, _ = v.partition(":")
					print(">>> The vector is for " + vec)
					vuln_vectors.append(vec)

		vuln_urls = {rank: []}
		for i in range(0, len(vuln_pages)):
			data = vuln_pages[i] + "?" + vuln_vectors[i] + "="
			_logger.info(data)
			vuln_urls[rank].append(data)
		return vuln_urls

	def threadCallback(self, request, result):
		#_logger.info("%s" % json.dumps(result))
		self.final_urls.update(result)

	def writeToFile(self):
		fp = open(self._output_path, "w")
		for k in sorted(self.final_urls.keys()):
			fp.write(">>> %d\n" % k)
			for url in self.final_urls[k]:
				fp.write(url)
				fp.write("\n")
		# json.dump(self.final_urls, fp)
		fp.close()


class Payload(object):
	def __init__(self):
		_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		_tim_evaluate_dir = os.path.dirname(_dir)
		_xsstrike_dir = os.path.join(os.path.dirname(_tim_evaluate_dir), "XSStrike")
		self._cmd_path = os.path.join(_xsstrike_dir, "xsstrike.py")
		print(self._cmd_path)

		self._thread_num = 8

		# input
		self._output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vuln_subdomains")
		self._input_path = os.path.join(self._output_dir, "subdomains_with_vector")

		self._indicator = ">>> "
		self._fuzzer_passed = "[passed]"

		# read input urls
		self.readUrls()

	def readUrls(self):
		_urls = {}
		cur_rank = -1

		with codecs.open(self._input_path, "r", "utf8") as f:
			for line in f.readlines():
				line = line.strip("\n")

				if self._indicator in line:
					_, _, rank = line.partition(self._indicator)
					cur_rank = int(rank)
				else:
					print("{}".format(line))
					if cur_rank not in _urls.keys():
						_urls[cur_rank] = []
					_urls[cur_rank].append(line)

		# duplicate
		self._input_urls = {}
		for k in _urls.keys():
			s = set()
			for url in _urls[k]:
				s.add(url)
			if len(s) > 0:
				self._input_urls[k] = []
				for u in s:
					self._input_urls[k].append(u)
		print(self._input_urls)

	def handleUrl(self, url, rank):
		print(" ".join(["python3", self._cmd_path, "-u", url, "--crawl"]))
		process_node = subprocess.Popen(["python3", self._cmd_path, "-u", url, "--fuzzer"],
										shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		vuln_payloads = []
		while process_node.poll() is None:
			line = process_node.stdout.readline()
			line = line.strip().decode("utf-8")
			if line:
				print('Subprogram output: [{}]'.format(line))
				if self._fuzzer_passed in line:
					_, _, v = line.partition(self._fuzzer_passed)
					v = v.strip("'").replace(" ", "")
					_logger.info(">>> [%d][%s] Find a passed payload: " % (rank, url) + v)
					vuln_payloads.append(v)

		return vuln_payloads

	def runForPayload(self):
		# the process pool
		pool = multiprocessing.Pool(self._thread_num)
		results = []
		for k in sorted(self._input_urls.keys()):
			for u in self._input_urls[k]:
				results.append(pool.apply_async(self.handleUrl, (u, k,)))

		pool.close()
		pool.join()


def parseVector():
	min_rank = 2000
	max_rank = 5000
	p = Parse(min_rank, max_rank)
	p.runForVector()


def generatePayload():
	Payload().runForPayload()


if __name__ == '__main__':
	# parseVector()
	generatePayload()
