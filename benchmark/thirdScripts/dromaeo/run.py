# coding=utf-8

'''
    Test the performance for Dromaeo benchamrk: https://dromaeo.uplinklabs.net/?dom
    Make sure your commit for Chromium is abab9d03f5c98e001f3403dd6fb1f4e637ef3a22
'''


import os
import shutil
import time
from utils.globalDefinition import _cache_for_Chrome_filepath, _node_run_url_filename_kraken
from utils.globalDefinition import _node_run_url_filename, _node_run_url_filename_dromeao
from utils.globalDefinition import _timeout_for_node_kraken_benchmark, _timeout_for_node
from utils.globalDefinition import _chrome_binary_normal, _chrome_binary
from benchmark.thirdScripts.dromaeo.globalDefinition import _CASES, _CASE_KEY_CHROME, _CASES_CONFIG
from run_script.run import RunUrl
from run_script.globalDefinition import *
from utils.executor import getTime


class RunChromeForPerformance(object):
    def __init__(self, in_url="http://serenityos.org/dromaeo/?dom",
                 in_chrome_binary=_chrome_binary, in_type="normal", in_round_index=0):
        self.test_url = in_url
        self.chrome_binary = in_chrome_binary
        self.round_index = in_round_index

        self.node_filename = _node_run_url_filename_dromeao

        _dir = os.path.abspath(os.path.dirname(__file__))
        self._results_tree_dir = os.path.join(_dir, "results")
        if not os.path.exists(self._results_tree_dir):
            os.mkdir(self._results_tree_dir)
        self._results_dir = os.path.join(self._results_tree_dir, "results-" + in_type)
        if os.path.exists(self._results_dir):
            shutil.rmtree(self._results_dir)
        os.mkdir(self._results_dir)

        self.log_path = os.path.join(self._results_tree_dir, "results.log")

        # the file to save the results of benchmark
        self._result_filepath = os.path.join(_dir, "dromaeo_node_results_" + in_type)
        if self.round_index == 0:
            fd = open(self._result_filepath, "w")
            fd.close()

    def run(self):

        with open(self._result_filepath, "a") as f:
            print(">>> the %d rounds" % self.round_index)
            f.write(">>> the %d rounds\n" % self.round_index)

            r = RunUrl(self.test_url, self.log_path, node_filename=self.node_filename,
                       timeout=_timeout_for_node_kraken_benchmark,
                       timeout_for_node=_timeout_for_node_kraken_benchmark,
                       chrome_binary=self.chrome_binary)
            if r.flag != CHROME_RUN_FLAG_DROMAEO_SUCCESS:
                print(">>> Timeout when running Chrome, retry it later...")
                return False
            f.write(r._results_for_dromeao + "\n\n\n")
        return True

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
                   chrome_binary=self.chrome_binary)
        time.sleep(5)
        return r.flag

    def clearChrome(self):
        while True:
            if self.clearChromeInternal() == CHROME_RUN_FLAG_SUCCESS:
                return


def run():
    _round = 1000
    for i in range(0, _round):
        print(">>> round: ", i)
        for case in _CASES:
            print(">>> case: ", case)
            p = RunChromeForPerformance(in_chrome_binary=_CASES_CONFIG[case][_CASE_KEY_CHROME],
                                        in_type=case,
                                        in_round_index=i)
            while True:
                if p.run():
                    break


