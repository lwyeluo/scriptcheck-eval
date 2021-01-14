# coding=utf-8

import os, re
from benchmark.thirdScripts.security_monitor.globalDefinition import _CASE_BASELINE, _CASE_OURS, _CASES
from benchmark.thirdScripts.security_monitor.globalDefinition import _TASK_RISKY, _TASK_NORMAL, _TASK_TYPE
from benchmark.thirdScripts.security_monitor.utils import *


class ParseLog(object):
    def __init__(self, filepath):
        self.filepath = filepath

        # features
        self._features_security_monitor_reg =  r".*SCRIPTCHECKER\] (.*)\[is_risky_task, cpu_cycle, time\] = (.*), (.*), ([\d]*)(.*)"

        self.results = ResultsForOneLog(in_filepath=filepath)

    def parse(self):
        print(">>> Handle %s" % self.filepath)

        with open(self.filepath, "r", encoding="ISO-8859-1") as f:
            content = f.readlines()

            for line in content:
                line = line.strip("\n")

                # match the feature of security monitor
                obj = re.match(self._features_security_monitor_reg, line)
                if obj:
                    monitor, is_risky, cpu, time_in_us, remain = obj.group(1), obj.group(2), obj.group(3), obj.group(4), obj.group(5)
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

                self.all_results.Add(case, p.results)

    def run(self):
        self.parse()
        self.all_results.RecordRawData()
        self.all_results.Merge()
        self.all_results.RecordFinalResult()


def run():
    Parse().run()
