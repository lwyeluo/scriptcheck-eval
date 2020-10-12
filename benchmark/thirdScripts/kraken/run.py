# coding=utf-8

'''
    Test the performance for kranken benchamrk: https://krakenbenchmark.mozilla.org/kraken-1.1/driver
    Make sure your commit for Chromium is abab9d03f5c98e001f3403dd6fb1f4e637ef3a22
'''


import os
import shutil
import time
from utils.globalDefinition import _cache_for_Chrome_filepath, _node_run_url_filename_kraken, _node_run_url_filename
from utils.globalDefinition import _timeout_for_node_kraken_benchmark, _timeout_for_node
from utils.globalDefinition import _chrome_binary_normal, _chrome_binary
from utils.globalDefinition import _NORMAL_, _TIM_
from run_script.run import RunUrl
from run_script.globalDefinition import *
from utils.executor import getTime


class RunChromeForPerformance(object):
    def __init__(self, in_url="https://krakenbenchmark.mozilla.org/kraken-1.1/driver",
                 in_chrome_binary=_chrome_binary, in_type="normal"):
        self.test_url = in_url
        self.chrome_binary = in_chrome_binary

        self.node_filename = _node_run_url_filename_kraken

        _dir = os.path.abspath(os.path.dirname(__file__))
        self._results_tree_dir = os.path.join(_dir, "results")
        if not os.path.exists(self._results_tree_dir):
            os.mkdir(self._results_tree_dir)
        self._results_dir = os.path.join(self._results_tree_dir, "results-" + in_type)
        if os.path.exists(self._results_dir):
            shutil.rmtree(self._results_dir)
        os.mkdir(self._results_dir)

        # the file to save the results of kraken benchmark
        self._result_filepath = os.path.join(_dir, "kraken_node_results_" + in_type)

        self._round = 20

    def run(self):

        with open(self._result_filepath, "w") as f:

            for i in range(0, self._round):

                filepath = os.path.join(self._results_dir, getTime())

                print(">>> the %d round, the filepath is %s" % (i, filepath))
                f.write(">>> the %d round, the filepath is %s" % (i, filepath))

                r = RunUrl(self.test_url, filepath, node_filename=self.node_filename,
                           timeout=_timeout_for_node_kraken_benchmark,
                           timeout_for_node=_timeout_for_node_kraken_benchmark,
                           chrome_binary=self.chrome_binary)
                f.write(r._results_for_kraken + "\n\n\n")

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
    in_chrome_type = {
        _TIM_: _chrome_binary,
        _NORMAL_: _chrome_binary_normal
    }
    # test normal chrome
    r = RunChromeForPerformance(in_chrome_binary=in_chrome_type[_NORMAL_],
                                in_type=_NORMAL_)
    r.clearChrome()
    r.run()
    # test the modified chrome
    r = RunChromeForPerformance(in_chrome_binary=in_chrome_type[_TIM_],
                                in_type=_TIM_)
    r.clearChrome()
    r.run()


