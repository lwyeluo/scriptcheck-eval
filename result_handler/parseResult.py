import os
import subprocess
import time
import re
import logging

from finalResult import FinalResult, FinalResultList

_dir = os.path.abspath(os.path.dirname(__file__))
_top_site_dir = os.path.join(os.path.dirname(_dir), "top-sites")
_log_filename = os.path.join(_dir, "result.log")
_result_dir = os.path.join(_dir, "tim-results")
print(_top_site_dir)

def outputAtConsole():
    logging.basicConfig(level=logging.DEBUG, format='%(message)s', filename=_log_filename, filemode="w")

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(logging.Formatter("%(message)s"))
    logging.getLogger('').addHandler(console)

# execute a shell command and block!
def execute(cmd):
	(status, output) = subprocess.getstatusoutput(cmd)
	if status != 0:
		raise Exception("[ERROR] failed to execute " + cmd + " . The status is " + str(status))
	return output

def executeWithoutCheckStatus(cmd):
	(status, output) = subprocess.getstatusoutput(cmd)
	return output

# get the timestamp
def getTime():
	return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

class Parse(object):
    def __init__(self):
        self._results_dir = _result_dir

        self._final_url_filename = os.path.join(_top_site_dir, "final_url")

        self._feature = "updated frame chain"

    def matchFrameChain(self, frame_chain):
        ret = []
        reg = "-(\d{1,}:\d{1,})_([^\s/]+://[^\s/]+/)(.*)"
        m = re.match(reg, frame_chain)
        if m:
            frame_id, origin, remain = m.group(1), m.group(2), m.group(3)
            ret.append({
                'id': frame_id,
                'origin': origin
            })
            if remain != "":
                ret += self.matchFrameChain(remain)
        return ret

    def handle(self, file_name):
        print(">>> HANDLE %s" % file_name)
        f = open(file_name, "r", encoding="ISO-8859-1")

        vuln_frames = [] # the frame chain whose size >= 2
        vuln_cross_origin_frames = [] # the frame chain which has multiple origins
        max_len_of_frame_chain = 0 # the max length of frame chains

        for line in f.readlines():
            line = line.strip("\n")
            if self._feature in line:
                line = line[line.index(self._feature) : ]
                _, _, remain = line.partition("=")
                if remain == "":
                    continue
                frame_chain = remain.split(',')[1].strip(' ')
                if frame_chain == "":
                    continue
                frames = self.matchFrameChain(frame_chain)
                # update the max size of frame chain
                if len(frames) > max_len_of_frame_chain:
                    max_len_of_frame_chain = len(frames)
                # for frame chain whose size is 1, we ignore it
                if len(frames) < 2:
                    continue
                # record frame chain whose size >= 2
                vuln_frames.append(frames)
                # record frame chain which has multiple origins
                origins = []
                for frame in frames:
                    if frame['origin'] not in origins:
                        origins.append(frame['origin'])
                    if len(origins) > 1:
                        vuln_cross_origin_frames.append(frames)
                        break

        f.close()

        return vuln_frames, vuln_cross_origin_frames, max_len_of_frame_chain

    def run(self):

        final_results = [] # store the final results

        with open(self._final_url_filename, 'r') as f:
            lines = f.readlines()
            for line in lines:

                log = line.strip("\n").split('\t')
                rank, url = log[0], log[1]
                idx = url.find("://")
                if idx >= 0:
                    domain = url[idx + 3 : ]
                else:
                    domain = url

                if rank[0] == '#':
                    ret = FinalResult(domain=domain, reachable=False, rank=rank[1:], url=url)
                    final_results.append(ret)
                    continue
                
                print("\n\n\t\t[RANK, URL, DOMAIN] = [%s, %s, %s]\n" % (rank, url, domain))
                
                # load all logs for that domain
                ret_dir = os.path.join(self._results_dir, domain)
                if os.path.exists(ret_dir) and os.path.isdir(ret_dir):
                    files = os.listdir(ret_dir)

                    ret = FinalResult(domain=domain, reachable=True, rank=rank, url=url)

                    for ret_file in files:
                        vuln_frames, vuln_cross_origin_frames, max_len_of_frame_chain = self.handle(os.path.join(ret_dir, ret_file))

                        ret.appendMaxFrameChain(max_len_of_frame_chain)
                        ret.appendCrossOriginFrameChains(vuln_cross_origin_frames)
                        ret.appendResultFileName(ret_file)

                    ret.collectMetadata()
                    final_results.append(ret)
				
            f.close()

        return final_results

if __name__ == '__main__':
    outputAtConsole()

    final_results = Parse().run()

    # log
    output = FinalResultList(final_results, logging)
    output.printRawDataTable()
    output.printDistributionTable()
    output.printCrossOriginDomains()
