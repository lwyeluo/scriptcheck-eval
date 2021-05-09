# coding=utf-8

'''
    Test the performance for top 10 JS libraries: https://hexometer.com/most-popular-tech-stacks/JavaScript+Libraries
    Make sure your commit for Chromium is 7501b47f7d81e9388a0bbc61c00a136ed0a3daee
'''


import os
import shutil
import time
from utils.globalDefinition import _node_run_url_filename, _cache_for_Chrome_filepath, _node_filename, _node_run_url_filename_delay
from utils.globalDefinition import _timeout_benchmark, _timeout_for_node_benchmark
from utils.globalDefinition import _chrome_binary_normal, _chrome_binary
from run_script.run import RunUrl
from run_script.globalDefinition import *
from utils.executor import getTime
from benchmark.thirdScripts.top10.parseResult import ParseLog
from benchmark.thirdScripts.top10.globalDefinition import NORMAL, TIM, IN_SITES


class RunChromeForPerformance(object):
    def __init__(self, in_site, in_url, in_chrome_binary=_chrome_binary, in_type="normal"):
        self.test_url = in_url
        self.chrome_binary = in_chrome_binary

        self.site = in_site

        self.node_filename = _node_run_url_filename_delay

        _dir = os.path.abspath(os.path.dirname(__file__))
        self._results_tree_dir = os.path.join(_dir, "results")
        if not os.path.exists(self._results_tree_dir):
            os.mkdir(self._results_tree_dir)
        self._results_dir = os.path.join(self._results_tree_dir, "results-"+in_site+"-"+in_type)
        if os.path.exists(self._results_dir):
            shutil.rmtree(self._results_dir)
        os.mkdir(self._results_dir)

        self._round = 500 

    def run(self):

        for i in range(0, self._round):

            while True:
                filepath = os.path.join(self._results_dir, str(i))

                print(">>> the %d round, the filepath is %s" % (i, filepath))

                RunUrl(self.test_url, filepath, node_filename=self.node_filename,
                       timeout=_timeout_benchmark, timeout_for_node=_timeout_for_node_benchmark,
                       chrome_binary=self.chrome_binary)

                p = ParseLog(filepath, site=self.site)
                p.run()
                print(p.results)
                if len(p.results) > 0:
                    break

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
                   timeout=_timeout_benchmark, timeout_for_node=_timeout_for_node_benchmark,
                   chrome_binary=self.chrome_binary)
        time.sleep(5)
        return r.flag

    def clearChrome(self):
        while True:
            if self.clearChromeInternal() == CHROME_RUN_FLAG_SUCCESS:
                return


def runSite(site):
    in_chrome_type = {
        TIM: _chrome_binary,
        NORMAL: _chrome_binary_normal
    }
    # test normal chrome
    r = RunChromeForPerformance(in_site=site,
                                in_url=IN_SITES[site][NORMAL],
                                in_chrome_binary=in_chrome_type[NORMAL],
                                in_type=NORMAL)
    r.clearChrome()
    r.run()
    # test the modified chrome
    r = RunChromeForPerformance(in_site=site,
                                in_url=IN_SITES[site][TIM],
                                in_chrome_binary=in_chrome_type[TIM],
                                in_type=TIM)
    r.clearChrome()
    r.run()


def run(site):
    if site:
        runSite(site)
    else:
        for site in IN_SITES.keys():
            print(">>>>>>>>>>>> test SITE: " + site)
            runSite(site)

