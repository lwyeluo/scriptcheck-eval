# coding=utf-8

'''
    Test the performance for top 10 JS libraries: https://hexometer.com/most-popular-tech-stacks/JavaScript+Libraries
    Make sure your commit for Chromium is 7501b47f7d81e9388a0bbc61c00a136ed0a3daee
'''


import os
import shutil
import time
from utils.globalDefinition import _node_run_url_filename, _cache_for_Chrome_filepath, _node_run_url_filename_delay
from utils.globalDefinition import _node_run_url_filename_library
from utils.globalDefinition import _timeout_benchmark, _timeout_for_node_benchmark
from utils.globalDefinition import _chrome_binary_normal, _chrome_binary
from run_script.run import RunUrl
from run_script.globalDefinition import *
from benchmark.thirdScripts.library.globalDefinition import _CASES, _CASE_KEY_CHROME, _CASES_CONFIG, IN_SITES, SITE_URL


class RunChromeForPerformance(object):
    def __init__(self, in_site, in_url, in_chrome_binary=_chrome_binary, in_type="normal",
                 in_log_dir="results/", in_round_index=0):
        self.test_url = in_url
        self.chrome_binary = in_chrome_binary
        self.log_dir = in_log_dir
        self.log_path = os.path.join(in_log_dir, "results.log")

        self.site = in_site
        self.type = in_type
        self.round_index = in_round_index

        self.node_filename = _node_run_url_filename_library

        # the file to save the results of benchmark
        self._result_filepath = os.path.join(self.log_dir, "%s_node_results_%s" % (self.site, self.type))
        if self.round_index == 0:
            fd = open(self._result_filepath, "w")
            fd.close()

    def run(self):
        with open(self._result_filepath, "a") as f:
            print(">>> the %d rounds" % self.round_index)
            f.write(">>> the %d rounds\n" % self.round_index)

            while True:
                r = RunUrl(self.test_url, self.log_path, node_filename=self.node_filename,
                           timeout=_timeout_benchmark, timeout_for_node=_timeout_for_node_benchmark,
                           chrome_binary=self.chrome_binary)

                if r.flag != CHROME_RUN_FLAG_3RD_LIBRARY_SUCCESS:
                    print(">>> Timeout when running Chrome, retry it later...")
                else:
                    f.write(r._results_for_3rd_library + "\n\n\n")
                    break
            f.close()

    '''
        Some caches for Chrome must be cleared, otherwise the latency for Chrome is too high
    '''
    def clearChromeInternal(self):
        if os.path.exists(_cache_for_Chrome_filepath):
            shutil.rmtree(_cache_for_Chrome_filepath)

        # run Chrome for the welcome webpage
        print(">>> Welcome to Chrome")
        r = RunUrl("https://www.baidu.com", self.log_path, node_filename=_node_run_url_filename,
                   timeout=_timeout_benchmark, timeout_for_node=_timeout_for_node_benchmark,
                   chrome_binary=self.chrome_binary)
        time.sleep(5)
        return r.flag

    def clearChrome(self):
        while True:
            if self.clearChromeInternal() == CHROME_RUN_FLAG_SUCCESS:
                return


def runSite(site, round):
    _dir = os.path.abspath(os.path.dirname(__file__))
    _results_tree_dir = os.path.join(_dir, "results")
    if not os.path.exists(_results_tree_dir):
        os.mkdir(_results_tree_dir)

    for i in range(0, round):
        for case in _CASES:
            r = RunChromeForPerformance(in_site=site,
                                        in_url=SITE_URL[site][case],
                                        in_chrome_binary=_CASES_CONFIG[case][_CASE_KEY_CHROME],
                                        in_type=case,
                                        in_log_dir=_results_tree_dir,
                                        in_round_index=i)
            if i == 0:
                r.clearChrome()
            r.run()


def run(site):
    round = 100
    if site:
        runSite(site, round)
    else:
        for site in IN_SITES:
            print(">>>>>>>>>>>> test SITE: " + site)
            runSite(site, round)

