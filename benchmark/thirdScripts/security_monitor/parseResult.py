# coding=utf-8

import os, re
from benchmark.thirdScripts.security_monitor.globalDefinition import _CASE_BASELINE, _CASE_OURS, _CASES, _SECURITY_MONITOR_SETTIMEOUTWR
from benchmark.thirdScripts.security_monitor.globalDefinition import _TASK_RISKY, _TASK_NORMAL, _TASK_TYPE, _SECURITY_MONITOR_JS
from benchmark.thirdScripts.security_monitor.utils import *


class ParseLog(object):
    def __init__(self, filepath):
        self.filepath = filepath

        # features
        self._features_security_monitor_reg =  r".*SCRIPTCHECKER\] (.*)\[is_risky_task, cpu_cycle, time\] = (.*), (.*), ([\d]*)(.*)"

        self.results = ResultsForOneLog(in_filepath=filepath)

    def parse(self):
        print(">>> Handle %s" % self.filepath)

        isFirstSetTimeoutWR = True

        with open(self.filepath, "r", encoding="ISO-8859-1") as f:
            content = f.readlines()

            for line in content:
                line = line.strip("\n")

                # match the feature of security monitor
                obj = re.match(self._features_security_monitor_reg, line)
                if obj:
                    monitor, is_risky, cpu, time_in_us, remain = obj.group(1), obj.group(2), obj.group(3), obj.group(4), obj.group(5)
                    # skip the first time of setTimeoutWR
                    if monitor == _SECURITY_MONITOR_SETTIMEOUTWR and isFirstSetTimeoutWR == True:
                        isFirstSetTimeoutWR = False
                        continue
                    # handle JS monitor
                    if monitor == _SECURITY_MONITOR_JS[:-1]:
                        monitor = _SECURITY_MONITOR_JS + remain.split(":")[2]
                    if not self.results.Add(monitor, float(is_risky), float(cpu), float(time_in_us), remain):
                        raise Exception("Cannot add data[%s] from log[%s]" % (line, self.filepath))
                    # print("\t\t>>> %s => {%s, %s, %s, %s}" % (line, monitor, is_risky, cpu, time_in_us))
                    continue
            f.close()

    def run(self):
        self.parse()
        self.results.Merge()


class Parse(object):
    def __init__(self):
        _dir = os.path.abspath(os.path.dirname(__file__))
        self._results_tree_dir = os.path.join(_dir, "results")

        self.all_results = ResultsForAllLogs()

    def parse(self):
        for case in _CASES:
            _tmp_dir = os.path.join(self._results_tree_dir, case)
            if not os.path.exists(_tmp_dir):
                raise Exception("DIR %s does not exist" % _tmp_dir)

            files = os.listdir(_tmp_dir)
            for i in range(0, len(files)-1):
                filepath = os.path.join(_tmp_dir, str(i))

                # parse the log
                p = ParseLog(filepath=filepath)
                p.run()

                # get the results
                if p.results.IsEmpty():
                    continue

                # print(p.results.ToString())
                if case == _CASE_OURS and (not p.results.IsValidForRiskyLog()):
                    raise Exception("LOG %s does not have enough data" % filepath)

                self.all_results.Add(case, p.results)

    def run(self):
        self.parse()
        self.all_results.RecordFilteredData()
        self.all_results.MergeFilteredByTime()
        self.all_results.RecordFinalResultFilteredByTime()


def run():
    Parse().run()
