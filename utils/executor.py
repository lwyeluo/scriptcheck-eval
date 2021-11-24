# coding=utf-8

import subprocess
import time


# execute a shell command and block!
def execute(cmd):
	(status, output) = subprocess.getstatusoutput(cmd)
	if status != 0:
		raise Exception("[ERROR] failed to execute " + cmd + " . The status is " + str(status) + ". output is " + str(output))
	return output


# execute a shell command and block!
def executeByList(cmd):
	if not isinstance(cmd, list):
		raise Exception("Use list!")
	p = subprocess.Popen(cmd, shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
	stdout, _ = p.communicate()
	return stdout.decode("utf-8")


def executeWithoutCheckStatus(cmd):
	(status, output) = subprocess.getstatusoutput(cmd)
	return output, status

# get the timestamp
def getTime():
	return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))