# coding=utf-8

'''
    Test the performance for Dromaeo benchamrk: https://dromaeo.uplinklabs.net/?dom
    Make sure your commit for Chromium is abab9d03f5c98e001f3403dd6fb1f4e637ef3a22
'''


import os
import shutil
import time
from utils.globalDefinition import _cache_for_Chrome_filepath, _node_run_url_filename_kraken
from utils.globalDefinition import _node_run_url_filename, _node_run_url_filename_delay
from utils.globalDefinition import _timeout_for_node_kraken_benchmark, _timeout_for_node
from utils.globalDefinition import _chrome_binary_normal, _chrome_binary
from run_script.run import RunUrl
from run_script.globalDefinition import *
from utils.executor import getTime
from benchmark.thirdScripts.sandbox_context.globalDefinition import _CASES_CONFIG, _CASE_KEY_URL, _CASE_KEY_CHROME, _CASE_OURS_CROSS


class RunChromeForPerformance(object):
    def __init__(self, in_url, in_chrome_binary, in_type):
        self.test_url = in_url
        self.chrome_binary = in_chrome_binary
        self.case_type = in_type

        print(self.test_url, self.chrome_binary, self.case_type)

        self.node_filename = _node_run_url_filename_delay

        _dir = os.path.abspath(os.path.dirname(__file__))
        self._results_tree_dir = os.path.join(_dir, "results")
        if not os.path.exists(self._results_tree_dir):
            os.mkdir(self._results_tree_dir)
        self._results_dir = os.path.join(self._results_tree_dir, "results-" + in_type)
        if os.path.exists(self._results_dir):
            shutil.rmtree(self._results_dir)
        os.mkdir(self._results_dir)

        self._round = 20

    def run(self):

        for i in range(0, self._round):

            filepath = os.path.join(self._results_dir, getTime())

            print(">>> the %d round for %s, the filepath is %s" % (i, self.case_type, filepath))

            r = RunUrl(self.test_url, filepath, node_filename=self.node_filename,
                       timeout=_timeout_for_node_kraken_benchmark,
                       timeout_for_node=_timeout_for_node_kraken_benchmark,
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

def run_cross():
    print(os.path.abspath(__file__))
    case = _CASE_OURS_CROSS
    r = RunChromeForPerformance(in_url=_CASES_CONFIG[case][_CASE_KEY_URL],
                                in_chrome_binary=_CASES_CONFIG[case][_CASE_KEY_CHROME],
                                in_type=case)
    r.clearChrome()
    r.run()

def run_except_cross():
    print(os.path.abspath(__file__))

    for case in _CASES_CONFIG.keys():
        if case == _CASE_OURS_CROSS:
            continue
        r = RunChromeForPerformance(in_url=_CASES_CONFIG[case][_CASE_KEY_URL],
                                    in_chrome_binary=_CASES_CONFIG[case][_CASE_KEY_CHROME],
                                    in_type=case)
        r.clearChrome()
        r.run()

def run():
    print(os.path.abspath(__file__))

    for case in _CASES_CONFIG.keys():
        r = RunChromeForPerformance(in_url=_CASES_CONFIG[case][_CASE_KEY_URL],
                                    in_chrome_binary=_CASES_CONFIG[case][_CASE_KEY_CHROME],
                                    in_type=case)
        r.clearChrome()
        r.run()


