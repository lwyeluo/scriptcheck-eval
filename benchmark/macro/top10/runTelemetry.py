# coding=utf-8

import os
import shutil
import subprocess
import signal
from threading import Timer
from utils.globalDefinition import _chrome_binary, _chrome_binary_normal
from benchmark.macro.top10.globalDefinition import _CASES, _CASES_CONFIG, _CASE_KEY_CHROME, printf
from utils.executor import executeWithoutCheckStatus
from benchmark.macro.top10.getJsonFromTelemetry import GetJSONFromTelemetry


class TelemetryRunner(object):
    def __init__(self, in_chrome_binary, in_type, in_round_index):
        self.case_type = in_type
        self.chrome_binary = in_chrome_binary
        self.round_index = in_round_index

        printf(">>> run for case[%s], Chrome is [%s]" % (in_type, in_chrome_binary))

        _dir = os.path.abspath(os.path.dirname(__file__))
        self._results_tree_dir = os.path.join(_dir, "results")
        if not os.path.exists(self._results_tree_dir):
            os.mkdir(self._results_tree_dir)
        self._results_dir = os.path.join(self._results_tree_dir, "results-" + in_type)
        printf("%s\t%s\t%s" % (in_chrome_binary, in_type, self._results_dir))
        if in_round_index == 0:
            if os.path.exists(self._results_dir):
                shutil.rmtree(self._results_dir)
            os.mkdir(self._results_dir)

        self.timeout = 30*60

        self.done_flag = True

        self._cmd_0, self._cmd_1, self._result_path = self.getTelemetryCmdAndResultPath()

    def getTelemetryCmdAndResultPath(self):
        _dir = self.chrome_binary
        for i in range(0, 3):
            _dir = os.path.dirname(_dir)
        _runner_path = _dir + "/tools/perf/run_benchmark"
        if not os.path.exists(_runner_path):
            raise Exception("Cannot find the file path of telemetry benchmark [%s] " % _runner_path)
        _result_path = _dir + "/tools/perf/results.html"

        _cmd_0 = "%s run page_cycler_v2.top_10_0 --browser-executable=%s --use-live-sites --show-stdout" % (_runner_path, self.chrome_binary)
        _cmd_1 = "%s run page_cycler_v2.top_10_1 --browser-executable=%s --use-live-sites --show-stdout" % (_runner_path, self.chrome_binary)
        printf(">>> prepare to execute: %s" % _cmd_0)
        printf(">>> prepare to execute: %s" % _cmd_1)
        return _cmd_0, _cmd_1, _result_path

    def timeoutCallback(self, process_node):
        self.done_flag = False
        printf("\t\tEnter timeoutCallback")
        try:
            os.killpg(process_node.pid, signal.SIGKILL)
        except Exception as error:
            printf(error)
        try:
            cmd = "kill -9 $(ps -ef | grep run_benchmark | awk '{print $2}')"
            stdout = executeWithoutCheckStatus(cmd)
            printf(stdout)
        except Exception as error:
            printf(error)

    def execute(self, _cmd):
        # 1. clear the results file
        if os.path.exists(self._result_path):
            os.remove(self._result_path)
        # 2. execute the cmd and wait it done
        process_node = subprocess.Popen(_cmd.split(' '), preexec_fn=os.setsid)
        # create a timer
        my_timer = Timer(self.timeout, self.timeoutCallback, [process_node])
        my_timer.start()

        process_node.communicate()

        my_timer.cancel()

    def run_benchmark(self, _cmd, idx):
        self.done_flag = True
        self.execute(_cmd)
        if not self.done_flag:
            return False
        # 3. save the results
        if not os.path.exists(self._result_path):
            return False
        _tmp_dir = os.path.join(self._results_dir, str(self.round_index))
        if not os.path.exists(_tmp_dir):
            os.mkdir(_tmp_dir)
        _html_path = os.path.join(_tmp_dir, "results_%d.html" % idx)
        shutil.copy(self._result_path, _html_path)

        # test if the results.html contains data
        _save_path = os.path.join(_tmp_dir, "results_%d.json" % idx)
        _download_filename = "results_%d.json" % idx
        _p = GetJSONFromTelemetry(in_html_path=_html_path,
                                  in_log_path=os.path.join(self._results_dir, "results.log"),
                                  in_save_path=_save_path,
                                  in_download_filename=_download_filename)
        if not _p.test():
            printf("ERROR: cannot get results.json from the benchmark results.")
            return False
        return True

    def run_all(self):
        while True:
            if self.run_benchmark(self._cmd_0, 0):
                break
        while True:
            if self.run_benchmark(self._cmd_1, 1):
                break

def run():
    _round = 10
    for i in range(0, _round):
        print(">>> round: ", i)
        for case in _CASES:
            print(">>> case: ", case)
            p = TelemetryRunner(in_chrome_binary=_CASES_CONFIG[case][_CASE_KEY_CHROME],
                                in_type=case,
                                in_round_index=i)
            p.run_all()
