# coding=utf-8

'''
    Test the performance for TIM
    Make sure your commit for Chromium is 642211e601dcd48240207df507b631fd1bc4b498, which
        adds the logs to record the CPU cycles and time usages
'''


import os
import shutil
import time
from utils.globalDefinition import _node_run_url_filename, _cache_for_Chrome_filepath, _node_filename
from utils.globalDefinition import _timeout_benchmark, _timeout_for_node_benchmark
from run_script.run import RunUrl
from utils.executor import getTime


class RunChromeForPerformance(object):
    def __init__(self):
        self.test_url = "https://news.yahoo.com"  # here is the web page which contains frame chain whose length is 99

        _dir = os.path.abspath(os.path.dirname(__file__))
        self._results_dir = os.path.join(_dir, "results")
        if os.path.exists(self._results_dir):
            shutil.rmtree(self._results_dir)
        os.mkdir(self._results_dir)

        self._round = 100

    def run(self):

        for i in range(0, self._round):

            filepath = os.path.join(self._results_dir, getTime())

            print(">>> the %d round, the filepath is %s" % (i, filepath))

            RunUrl(self.test_url, filepath, node_filename=_node_run_url_filename,
                   timeout=_timeout_benchmark, timeout_for_node=_timeout_for_node_benchmark)

    '''
        Some caches for Chrome must be cleared, otherwise the latency for Chrome is too high
    '''
    def clearChrome(self):
        if os.path.exists(_cache_for_Chrome_filepath):
            shutil.rmtree(_cache_for_Chrome_filepath)

        # run Chrome for the welcome webpage
        print(">>> Welcome to Chrome")
        filepath = os.path.join(self._results_dir, "test")
        RunUrl("https://news.yahoo.com", filepath, node_filename=_node_run_url_filename)

        time.sleep(5)


def run():
    r = RunChromeForPerformance()
    r.clearChrome()
    r.run()
