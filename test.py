import time
import subprocess  
import commands
import os
import time

# execute a shell command and block!
def execute(cmd):
	(status, output) = commands.getstatusoutput(cmd)
	if status != 0:
		raise Exception("[ERROR] failed to execute " + cmd + " . The status is " + str(status))
	return output

def executeWithoutCheckStatus(cmd):
	(status, output) = commands.getstatusoutput(cmd)
	return output

# get the timestamp
def getTime():
	return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

class TimTest(object):
	def __init__(self):
		# get the home directory
		self._home_dir = execute("echo $HOME")
		# get the chrome binary
		self._chrome_binary = self._home_dir + "/chromium/tick/src/out/Default/chrome"
		print(self._chrome_binary)
		# get the node binary
		self._node_binary = "node"
		# get the nodejs script
		self._node_filename = "Hello.js"

		self._url_filename = "url.txt"
		self._results_dir = self._home_dir + "/workspace/tim-results"

		# for each web page, we run 3 rounds
		self._round = 3

		# create an EMPTY directory to save results
		execute("rm -rf " + self._results_dir)
		execute("mkdir -p " + self._results_dir)

	def runPerUrl(self, url, ret_filename):
		ret_fd = open(ret_filename, 'w')

		p = subprocess.Popen([self._chrome_binary, '--remote-debugging-port=9222'], stderr=ret_fd, stdout=ret_fd)
		print('>>> START ' + url)
		time.sleep(2)
		print("****************node start********************************* ")
		ti = subprocess.Popen([self._node_binary, self._node_filename, url], stdout=subprocess.PIPE)
		print("****************node end*************************************")
		print(ti.stdout.read())
		print('>>> FINISH ' + url)

		time.sleep(5)
		executeWithoutCheckStatus("kill -9 $(ps -ef | grep chrome | awk '{print $2}')")

		ret_fd.close()

	def run(self):
		with open(self._url_filename, 'r') as f:
			lines = f.readlines()
			for line in lines:
				url = line.strip("\n")
				# create the directory for results
				ret_dir = self._results_dir + "/" + url
				execute("mkdir -p " + ret_dir)
				# run that url
				for i in range(0, self._round):
					self.runPerUrl('https://' + url, ret_dir + "/" + getTime())
			f.close()

if __name__ == '__main__':
	TimTest().run()
