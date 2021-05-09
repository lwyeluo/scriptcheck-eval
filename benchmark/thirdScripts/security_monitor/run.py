# coding=utf-8

'''
    Test the performance for DOM access
    Make sure your commit for Chromium is abab9d03f5c98e001f3403dd6fb1f4e637ef3a22
'''


import os
import shutil
import time
from utils.globalDefinition import _node_run_url_filename, _cache_for_Chrome_filepath, _node_run_url_filename_delay
from utils.globalDefinition import _timeout_benchmark, _timeout_for_node_benchmark
from run_script.run import RunUrl
from run_script.globalDefinition import *
from utils.executor import getTime
from benchmark.thirdScripts.security_monitor.globalDefinition import _CASES_CONFIG, _CASE_KEY_URL, _CASE_KEY_CHROME
from benchmark.thirdScripts.security_monitor.globalDefinition import _CASE_BASELINE, _CASE_OURS
from benchmark.thirdScripts.security_monitor.parseResult import ParseLog


class RunChromeForPerformance(object):
    def __init__(self, in_url, in_chrome_binary, in_results_dir, in_case, in_round_idx):
        self.test_url = in_url
        self.chrome_binary = in_chrome_binary

        self.node_filename = _node_run_url_filename_delay
        self._results_dir = in_results_dir

        self._case = in_case

        self._round = in_round_idx

        self.log_filepath = filepath = os.path.join(self._results_dir, str(self._round))

    def runOnce(self):
        print(">>> the %d round, the filepath is %s" % (self._round, self.log_filepath))

        RunUrl(self.test_url, self.log_filepath, node_filename=self.node_filename,
               timeout=_timeout_benchmark, timeout_for_node=_timeout_for_node_benchmark,
               chrome_binary=self.chrome_binary)

    def run(self):
        while True:
            self.runOnce()
            # check whether this round is successful
            p = ParseLog(filepath=self.log_filepath)
            p.run()
            if (self._case == _CASE_BASELINE) and (not p.results.IsEmpty()):
                return
            if (self._case == _CASE_OURS) and (not p.results.IsEmpty()) and (p.results.IsValidForRiskyLog()):
                return
            print("\twe cannot collect data in this round, so retry in this round...")

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
                   chrome_binary=self.chrome_binary)
        time.sleep(5)
        return r.flag

    def clearChrome(self):
        while True:
            if self.clearChromeInternal() == CHROME_RUN_FLAG_SUCCESS:
                return


def run():
    print(">>>>>>>>>>>> test security monitor overhead")
    _dir = os.path.abspath(os.path.dirname(__file__))
    _results_dir = os.path.join(_dir, "results")
    if os.path.exists(_results_dir):
        shutil.rmtree(_results_dir)
    os.mkdir(_results_dir)

    _round = 500
    for i in range(0, _round):
        print(">>> round: ", i)
        for case in _CASES_CONFIG.keys():
            _target_dir = os.path.join(_results_dir, case)
            r = RunChromeForPerformance(in_url=_CASES_CONFIG[case][_CASE_KEY_URL],
                                        in_chrome_binary=_CASES_CONFIG[case][_CASE_KEY_CHROME],
                                        in_results_dir=_target_dir,
                                        in_case=case,
                                        in_round_idx=i)
            if i == 0:
                if os.path.exists(_target_dir):
                    shutil.rmtree(_target_dir)
                os.mkdir(_target_dir)

                r.clearChrome()

            r.run()
