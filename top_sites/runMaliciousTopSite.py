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
from utils.regMatch import getSiteFromURL, strip_into_csv


class RunMaliciousTopSites(object):
    def __init__(self, file_suffix="blocked-sites"):

        # pls run firstly:
        #   python3 evaluate.py --run-alexa-top-sites
        #   python3 evaluate.py --parse-log --Alexa
        self._topsite_raw_data = os.path.join(_topsites_dir, "block_results_host_url.csv")

        self._results_dir = os.path.join(_topsites_dir, "results-%s" % file_suffix)
        self._results_crash_filename = os.path.join(_topsites_dir, "url-status-%s.csv" % file_suffix)
        self._crashed_urls = []

        # create an EMPTY directory to save results
        execute("rm -rf " + self._results_dir + " || true")
        execute("mkdir -p " + self._results_dir + " || true")

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
        fd = open(self._topsite_raw_data, "r")
        urls = fd.readlines()
        fd.close()

        rets = set()
        for i, url in enumerate(urls):
            rets.add(url.strip("\n"))

        return rets

    def run(self):
        fd = open(self._results_crash_filename, 'w')

        urls = self.getUrls()
        domains = set()

        page_idx = 0
        for i, url in enumerate(urls):
            site = getSiteFromURL(url)
            if site is None or site in domains:
                continue
            domains.add(site)

            # whether needs to clear cache
            if page_idx % 500 == 0:
                self.clearChromeInternal()
            page_idx += 1

            record_data = "%d,%s,%s," % (i + 1, strip_into_csv(site), strip_into_csv(url))

            # generate a unique name for the results
            filename = url.replace(".", "_").replace(":", "_").replace("/", "_")
            if len(filename) > 50:
                filename = filename[:50]

            filepath = os.path.join(self._results_dir, filename)
            print(">>> run", page_idx, i, site, url, filepath)

            # run Chrome with that url
            r = RunUrl(url, filepath, node_filename=_node_run_url_filename,
                       timeout_for_node=60)

            if r.flag == CHROME_RUN_FLAG_CRASH:
                print("!!!! this URL[%s] is crash!!!" % url)
                record_data += "Crash\n"
            elif r.flag == CHROME_RUN_FLAG_SUCCESS:
                print("!!!! this URL[%s] is success!!!" % url)
                record_data += "OK\n"
            elif r.flag == CHROME_RUN_FLAG_TIMEOUT:
                print("!!!! this URL[%s] is timeout!!!" % url)
                record_data += "Timeout\n"
            else:
                record_data += "Unknow-error-%d\n" % r.flag

            fd.write(record_data)
            fd.flush()

        fd.close()


def run():
    RunMaliciousTopSites().run()
