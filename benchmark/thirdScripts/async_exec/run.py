# coding=utf-8

'''
    Test the performance for async
    Make sure your commit for Chromium is abab9d03f5c98e001f3403dd6fb1f4e637ef3a22
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


class RunChromeForPerformance(object):
    def __init__(self, in_url, in_chrome_binary=_chrome_binary, in_type="normal"):
        self.test_url = in_url
        self.chrome_binary = in_chrome_binary

        self.node_filename = _node_run_url_filename_delay

        _dir = os.path.abspath(os.path.dirname(__file__))
        self._results_dir = os.path.join(_dir, "results")
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
        r = RunUrl("https://www.baidu.com", filepath, node_filename=_node_run_url_filename,
                   chrome_binary=self.chrome_binary)
        time.sleep(5)
        return r.flag

    def clearChrome(self):
        while True:
            if self.clearChromeInternal() == CHROME_RUN_FLAG_SUCCESS:
                return


def run():
    print(">>>>>>>>>>>> test ASYNC execution")
    p = RunChromeForPerformance(in_url="http://localhost:3001/taskPermission/async/index.html")
    p.clearChrome()
    p.run()

