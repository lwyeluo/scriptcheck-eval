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


class RunTopSites(object):
    def __init__(self):

        # the homepages for a domain
        self._homepage_file = os.path.join(_topsites_dir, "reachable_domains")
        # the urls for a domain
        self._urls_dir = os.path.join(_topsites_dir, "urls")
        # to save the Chrome's logs
        self._results_dir = os.path.join(_topsites_dir, "results")
        self._results_log_filename = os.path.join(_topsites_dir, "results-domain.log")
        # save the Chrome's logs for the last time running scritp
        self._results_dir_last_time = os.path.join(_topsites_dir, "results.bak")

        self._results_crash_filename = os.path.join(_topsites_dir, "crashed-url")
        self._crashed_urls = []

        # create an EMPTY directory to save results
        execute("rm -rf " + self._results_dir + " || true")
        execute("mkdir -p " + self._results_dir + " || true")

    '''
        Some caches for Chrome must be cleared, otherwise the latency for Chrome is too high
    '''
    def clearChromeInternal(self):
        if os.path.exists(_cache_for_Chrome_filepath):
            shutil.rmtree(_cache_for_Chrome_filepath)

        # run Chrome for the welcome webpage
        print(">>> Welcome to Chrome")
        filepath = os.path.join(self._results_dir, "test")
        r = RunUrl("https://www.baidu.com", filepath, node_filename=_node_run_url_filename,
                   timeout=_timeout_for_node,
                   timeout_for_node=_timeout_for_node,
                   chrome_binary=_chrome_binary)
        time.sleep(5)
        return r.flag

    def run(self):
        _logger.info(">>> initial file name is " + self._homepage_file)

        if not os.path.exists(self._urls_dir):
            raise Exception("Please run --crawl-url first")

        # the domains we have run last time
        have_run_domains = []
        if os.path.exists(self._results_dir_last_time):
            have_run_domains = os.listdir(self._results_dir_last_time)

        # transvers all domains
        sites = os.listdir(self._urls_dir)
        page_idx = 0
        for i, site in enumerate(sites):
            print(">>>>>>>>>>>>>>>> HANDLE the %d-th site: %s" % (i, site))
            # if we have run that site last time, we ignore it
            if site in have_run_domains:
                print(">>> %s has been checked, continue" % site)
                continue

            filepath = os.path.join(self._urls_dir, site)

            # results dir
            results_dir = os.path.join(self._results_dir, site)
            execute("mkdir -p " + results_dir + " || true")

            with open(filepath, 'r') as f:
                lines = f.readlines()

                for line in lines:
                    url = line.strip("\n").strip(' ')

                    # generate a unique name for the results
                    filename = url.replace(".", "_").replace(":", "_").replace("/", "_")
                    if len(filename) > 50:
                        filename = filename[:50]

                    _logger.info("[url, filename] = %s, %s" % (url, filename))

                    # whether needs to clear cache
                    if page_idx % 100 == 0:
                        self.clearChromeInternal()
                    page_idx += 1

                    # run Chrome with that url
                    r = RunUrl(url, results_dir + "/" + filename, node_filename=_node_run_url_filename,
                               timeout_for_node=60)

                    if r.flag == CHROME_RUN_FLAG_CRASH:
                        print("!!!! this URL[%s] is crash!!!" % url)
                        self._crashed_urls.append(url)

                    # collect the frame info for that url. See |RunUrl.frame_info|
                    _logger.info("######## frame info is: " + str(r.frame_info))
                    if r.frame_info and len(r.frame_info.keys()) > 1:
                        _logger.info("\t\t---> Multiple FRAMES")

                f.close()

        # save crashed urls
        with open(self._results_crash_filename, 'w') as fp:
            for url in self._crashed_urls:
                fp.write("%s\n" % url)

        # save logs
        execute("cp %s %s" % (_log_filename, self._results_log_filename))


def run():
    RunTopSites().run()
