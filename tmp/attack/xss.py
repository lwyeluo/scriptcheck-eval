import os
import json
import subprocess
import threadpool
import logging
import os
import multiprocessing

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
		self._output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vuln_subdomains")

		self._min_rank = min_rank
		self._max_rank = max_rank
		self._thread_num = 4

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
			self.final_urls.update(ret)

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
			line = str(line.strip())
			if line:
				print('Subprogram output: [{}]'.format(line))
				if self._xsstrike_vuln in line:
					_, _, v = line.partition(self._xsstrike_vuln)
					v = v.strip("'")
					print(">>> Find a vulnerable page: " + v)
					vuln_pages.append(v)
				elif self._xsstrike_vector in line:
					_, _, v = line.partition(self._xsstrike_vector)
					vec, _, _ = v.partition(":")
					print(">>> The vector is for " + vec)
					vuln_vectors.append(vec)

		vuln_urls = {rank: []}
		for i in range(0, len(vuln_pages)):
			print(vuln_pages[i], vuln_vectors[i])
			vuln_urls[rank].append("%s?%s=" % (vuln_pages[i], vuln_vectors[i]))
		_logger.info("%s" % json.dumps(result))
		return vuln_urls

	def threadCallback(self, request, result):
		#_logger.info("%s" % json.dumps(result))
		self.final_urls.update(result)

	def writeToFile(self):
		fp = open(self._output_path, "w")
		json.dump(self.final_urls, fp)
		fp.close()

if __name__ == '__main__':
	min_rank = 0
	max_rank = 20
	p = Parse(min_rank, max_rank)
	p.runForVector()
