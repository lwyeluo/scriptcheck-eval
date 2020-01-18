# coding=utf-8

'''
    Test the performance for top 10 JS libraries: https://hexometer.com/most-popular-tech-stacks/JavaScript+Libraries
    Make sure your commit for Chromium is c9c29de65565572280a2b4f80e6adbca40e4878d
'''


import os
import shutil
import time
from utils.globalDefinition import _node_run_url_filename, _cache_for_Chrome_filepath, _node_filename, _node_run_url_filename_delay
from utils.globalDefinition import _timeout_benchmark, _timeout_for_node_benchmark
from utils.globalDefinition import _chrome_binary_normal, _chrome_binary
from run_script.run import RunUrl
from utils.executor import getTime
from benchmark.thirdScripts.top10.globalDefinition import NORMAL, TIM, IN_SITES


class RunChromeForPerformance(object):
    def __init__(self, in_site, in_url, in_chrome_binary=_chrome_binary, in_type="normal"):
        self.test_url = in_url
        self.chrome_binary = in_chrome_binary

        if in_site == 'amcharts':
            self.node_filename = _node_run_url_filename_delay
        else:
            self.node_filename = _node_run_url_filename

        _dir = os.path.abspath(os.path.dirname(__file__))
        self._results_tree_dir = os.path.join(_dir, "results")
        if not os.path.exists(self._results_tree_dir):
            os.mkdir(self._results_tree_dir)
        self._results_dir = os.path.join(self._results_tree_dir, "results-"+in_site+"-"+in_type)
        if os.path.exists(self._results_dir):
            shutil.rmtree(self._results_dir)
        os.mkdir(self._results_dir)

        self._round = 20

    def run(self):

        for i in range(0, self._round):

            filepath = os.path.join(self._results_dir, getTime())

            print(">>> the %d round, the filepath is %s" % (i, filepath))

            RunUrl(self.test_url, filepath, node_filename=self.node_filename,
                   timeout=_timeout_benchmark, timeout_for_node=_timeout_for_node_benchmark,
                   chrome_binary=self.chrome_binary)

    '''
        Some caches for Chrome must be cleared, otherwise the latency for Chrome is too high
    '''
    def clearChromeInternal(self):
        if os.path.exists(_cache_for_Chrome_filepath):
            shutil.rmtree(_cache_for_Chrome_filepath)

        # run Chrome for the welcome webpage
        print(">>> Welcome to Chrome")
        filepath = os.path.join(self._results_dir, "test")
        r = RunUrl(self.test_url, filepath, node_filename=self.node_filename,
                   chrome_binary=self.chrome_binary)
        time.sleep(5)
        return r.flag

    def clearChrome(self):
        while True:
            if self.clearChromeInternal() == 0:
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

