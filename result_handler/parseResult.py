import os
import subprocess
import time
import re
import logging

_dir = os.path.abspath(os.path.dirname(__file__))
_top_site_dir = os.path.join(os.path.dirname(_dir), "top-sites")
_log_filename = os.path.join(_dir, "result.log")
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
        self._home_dir = execute("echo $HOME")

        self._results_dir = self._home_dir + "/workspace/tim-results"

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
        logging.info(">>> HANDLE %s" % file_name)
        f = open(file_name, "r", encoding="ISO-8859-1")

        vuln_frames = []
        vuln_cross_origin_frames = []

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
                if len(frames) < 2:
                    continue
                vuln_frames.append(frames)
                origins = []
                for frame in frames:
                    if frame['origin'] not in origins:
                        origins.append(frame['origin'])
                    if len(origins) > 1:
                        vuln_cross_origin_frames.append(frames)
                        break

        f.close()

        return vuln_frames, vuln_cross_origin_frames

    def run(self):

        total_websites, tested_websites, vuln_websites, vuln_cross_origin_websites = 0, 0, 0, 0
        vuln_cross_origin = []

        with open(self._final_url_filename, 'r') as f:
            lines = f.readlines()
            for line in lines:

                total_websites += 1

                if line[0] == '#':
                    continue
                log = line.strip("\n").split('\t')
                rank, url = log[0], log[1]
                domain = url[url.index("://") + 3 : ]
                logging.info("\n\n\t\t[RANK, URL, DOMAIN] = [%s, %s, %s]\n" % (rank, url, domain))

                tested_websites += 1
                
                # load all logs for that domain
                ret_dir = os.path.join(self._results_dir, domain)
                if os.path.exists(ret_dir) and os.path.isdir(ret_dir):
                    files = os.listdir(ret_dir)
                    is_vuln, is_cross_origin_vuln = False, False
                    for ret_file in files:
                        vuln_frames, vuln_cross_origin_frames = self.handle(os.path.join(ret_dir, ret_file))
                        if vuln_frames:
                            [logging.info(frame) for frame in vuln_frames]
                            is_vuln = True
                        if vuln_cross_origin_frames:
                            is_cross_origin_vuln = True
                            logging.info("!!!!!!!!!!!!! CROSS_ORIGIN_VULN !!!!!!!!!!!!!")
                    
                    if is_vuln:
                        vuln_websites += 1
                    if is_cross_origin_vuln:
                        vuln_cross_origin_websites += 1
                        vuln_cross_origin.append(domain)
				
            f.close()

        return total_websites, tested_websites, vuln_websites, vuln_cross_origin_websites, vuln_cross_origin

if __name__ == '__main__':
    outputAtConsole()

    total_websites, tested_websites, vuln_websites, vuln_cross_origin_websites, vuln_cross_origin = Parse().run()

    logging.info("\n\n\t\t[FINAL RESULTS]")
    logging.info("total_websites, tested_websites, vuln_websites, vuln_cross_origin_websites = %d, %d, %d, %d " %
        (total_websites, tested_websites, vuln_websites, vuln_cross_origin_websites))
    logging.info("vuln_rate = vuln/tested = %f%%" % ((vuln_websites / tested_websites) * 100))
    logging.info("vuln_rate(cross_origin) = vuln(cross)/tested = %f%%" % ((vuln_cross_origin_websites / tested_websites) * 100))
    logging.info("vuln_cross_origin_sites:")
    logging.info(str("\t".join(vuln_cross_origin)))
