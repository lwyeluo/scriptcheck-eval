# coding=utf-8

import os
import shutil
from utils.executor import *
from run_script.run import RunUrl

from utils.globalDefinition import _topsites_dir, _log_filename
from run_script.globalDefinition import *
from utils.logger import _logger

from utils.globalDefinition import _cache_for_Chrome_filepath, _node_run_url_filename_kraken
from utils.globalDefinition import _node_run_url_filename, _node_run_url_filename_dromeao
from utils.globalDefinition import _timeout_for_node_kraken_benchmark, _timeout_for_node
from utils.globalDefinition import _chrome_binary_normal, _chrome_binary
from utils.regMatch import getSiteFromURL


class RunMaliciousTopSites1(object):
    def __init__(self, file_suffix="blocked-sites"):

        # pls run firstly:
        #   python3 evaluate.py --run-alexa-top-sites
        #   python3 evaluate.py --parse-log --Alexa
        self._topsite_raw_data = os.path.join(_topsites_dir, "block_results_host_url.csv")

        self._results_dir = os.path.join(_topsites_dir, "results-%s" % file_suffix)
        self._results_crash_input_filename = os.path.join(_topsites_dir, "crashed-url-%s.csv" % file_suffix)
        self._crashed_urls = []

        if not os.path.exists(self._topsite_raw_data) \
            or not os.path.exists(self._results_dir):
            raise Exception("you should run alexa-top-sites and parse-log firstly")

    '''
        Some caches for Chrome must be cleared, otherwise the latency for Chrome is too high
    '''
    def clearChromeInternal(self):
        if os.path.exists(_cache_for_Chrome_filepath):
            shutil.rmtree(_cache_for_Chrome_filepath)

        # run Chrome for the welcome webpage
        print(">>> Welcome to Chrome")
        filepath = os.path.join(self._results_dir, "test")
        r = RunUrl("https://www.google.com", filepath, node_filename=_node_run_url_filename,
                   timeout=_timeout_for_node,
                   timeout_for_node=_timeout_for_node,
                   chrome_binary=_chrome_binary)
        time.sleep(5)
        return r.flag

    def getUrls(self):
        fd = open(self._results_crash_input_filename, "r")
        urls = fd.readlines()
        fd.close()

        rets = set()
        for i, url in enumerate(urls):
            rets.add(url.strip("\n"))

        return rets

    def run(self):
        fd = open(self._results_crash_input_filename, "r")
        content = fd.readlines()
        fd.close()

        page_idx = 0
        fd = open(self._results_crash_input_filename, "w")
        for i, line in enumerate(content):
            data = line.strip("\n")
            if data.endswith(",Done"):
                fd.write(line)
                continue
            data, _, status = data.rpartition(",")
            rank, _, url = data.partition(",")
            print(line)
            print(">>", rank, url)

            if page_idx % 500 == 0:
                self.clearChromeInternal()
            page_idx += 1

            # generate a unique name for the results
            filepath = os.path.join(self._results_dir, "%d" % i)
            print(">>> run", i, url, filepath)

            # run Chrome with that url
            r = RunUrl(url, filepath, node_filename=_node_run_url_filename,
                       timeout_for_node=30)

            if r.flag == CHROME_RUN_FLAG_CRASH:
                print("!!!! this URL[%s] is crash!!!" % url)
                fd.write("%s,Crash\n" % data)
            else:
                fd.write("%s,Done\n" % data)

        fd.close()
        print("hello")
        return


def run():
    RunMaliciousTopSites1().run()
