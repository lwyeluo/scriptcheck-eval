# coding=utf-8

import json, os
import numpy as np
from benchmark.thirdScripts.security_monitor.globalDefinition import _KEY_EVENTS_IN_CHROMIUM, _TASK_TYPE, _CASES
from benchmark.thirdScripts.security_monitor.globalDefinition import _CPU_CYCLE, _TIME_IN_US, _TASK_RISKY, _TASK_NORMAL
from benchmark.thirdScripts.security_monitor.globalDefinition import _SECURITY_MONITOR_DOM, _SECURITY_MONITOR_DOM_TARGET_ID
from benchmark.thirdScripts.security_monitor.globalDefinition import _OUTPUT_FILE_NAME, _CASE_BASELINE, _CASE_OURS
from benchmark.thirdScripts.security_monitor.globalDefinition import _SECURITY_MONITOR_TYPE_IN_CHROMIUM, _SECURITY_MONITOR_SETTIMEOUTWR


class ResultsForOneLog(object):
    def __init__(self, in_filepath):
        self.data = self.Alloc()
        self.filepath = in_filepath

        self.has_data = False

    # allocate a data to save results parsed from one log
    def Alloc(self):
        _results = {}
        for monitor in _KEY_EVENTS_IN_CHROMIUM:
            _results[monitor] = {}
            for task_type in _TASK_TYPE:
                _results[monitor][task_type] = {_CPU_CYCLE: [], _TIME_IN_US: []}
        return _results

    def Add(self, in_monitor, in_is_risky, in_cpu, in_time, in_remain):
        task_type = _TASK_RISKY if in_is_risky else _TASK_NORMAL
        if in_monitor not in self.data.keys() or task_type not in self.data[in_monitor].keys():
            return False
        # only the dom for target id is recorded
        if in_monitor == _SECURITY_MONITOR_DOM and _SECURITY_MONITOR_DOM_TARGET_ID not in in_remain:
            return True
        self.data[in_monitor][task_type][_CPU_CYCLE].append(in_cpu)
        self.data[in_monitor][task_type][_TIME_IN_US].append(in_time)
        self.has_data = True
        return True

    def Merge(self):
        if self.IsEmpty():
            return
        _tmp_data = self.Alloc()
        for monitor in _KEY_EVENTS_IN_CHROMIUM:
            for task_type in _TASK_TYPE:
                cpu = self.data[monitor][task_type][_CPU_CYCLE]
                time = self.data[monitor][task_type][_TIME_IN_US]
                _tmp_data[monitor][task_type][_CPU_CYCLE] = np.mean(cpu)
                _tmp_data[monitor][task_type][_TIME_IN_US] = np.mean(time)
        self.data = _tmp_data

    def ToString(self):
        return json.dumps(self.data)

    def IsEmpty(self):
        return not self.has_data

    def IsValidForRiskyLog(self):
        for monitor in _KEY_EVENTS_IN_CHROMIUM:
            if monitor == _SECURITY_MONITOR_SETTIMEOUTWR:
                # setTimeout maybe created by unrestricted task
                if np.isnan(self.data[monitor][_TASK_NORMAL][_CPU_CYCLE]) and \
                    np.isnan(self.data[monitor][_TASK_RISKY][_CPU_CYCLE]):
                    print("\t\twrong data:", monitor, self.data[monitor][_task_type][_CPU_CYCLE])
                    return False
            else:
                _task_type = _TASK_RISKY
                if np.isnan(self.data[monitor][_task_type][_CPU_CYCLE]):
                    print("\t\twrong data:", monitor, self.data[monitor][_task_type][_CPU_CYCLE])
                    return False
        return True

    def Get(self):
        return self.data


class ResultsForAllLogs:
    def __init__(self):
        self.data = self.Alloc()
        self.round = {}
        for case in _CASES:
            self.round[case] = 0
        self.output_file = os.path.join(os.path.dirname(__file__), _OUTPUT_FILE_NAME)


    def Alloc(self):
        _results = {}
        for monitor in _KEY_EVENTS_IN_CHROMIUM:
            _results[monitor] = {}
            for case in _CASES:
                _results[monitor][case] = {}
                for task_type in _TASK_TYPE:
                    _results[monitor][case][task_type] = {_CPU_CYCLE: [], _TIME_IN_US: []}
        return _results

    def Add(self, case, resultsForOneLog):
        if case not in _CASES:
            return False
        if resultsForOneLog.IsEmpty():
            print("\t\twithout data in %s" % resultsForOneLog.filepath)
        self.round[case] += 1
        in_data = resultsForOneLog.Get()
        for monitor in _KEY_EVENTS_IN_CHROMIUM:
            for task_type in _TASK_TYPE:
                cpu = in_data[monitor][task_type][_CPU_CYCLE]
                time = in_data[monitor][task_type][_TIME_IN_US]
                self.data[monitor][case][task_type][_CPU_CYCLE].append(cpu)
                self.data[monitor][case][task_type][_TIME_IN_US].append(time)
        # print(self.ToString())
        return True

    def ToString(self):
        return json.dumps(self.data)

    def RecordRawData(self):
        _round = 0
        for case in _CASES:
            if _round == 0:
                _round = self.round[case]
            elif _round != self.round[case]:
                raise Exception("Bad round")

        with open(self.output_file, 'w') as f:
            f.write("round\t")
            for monitor in _KEY_EVENTS_IN_CHROMIUM:
                f.write("%s" % monitor)
                f.write("\t" * len(_CASES) * len(_TASK_TYPE) * 2)
            f.write("\n\t")
            for monitor in _KEY_EVENTS_IN_CHROMIUM:
                for case in _CASES:
                    f.write("%s" % case)
                    f.write("\t" * len(_TASK_TYPE) * 2)
            f.write("\n\t")
            for monitor in _KEY_EVENTS_IN_CHROMIUM:
                for case in _CASES:
                    for task_type in _TASK_TYPE:
                        f.write("%s" % task_type)
                        f.write("\t" * 2)
            f.write("\n\t")
            for monitor in _KEY_EVENTS_IN_CHROMIUM:
                for case in _CASES:
                    for task_type in _TASK_TYPE:
                        f.write("%s\t%s\t" % (_CPU_CYCLE, _TIME_IN_US))

            f.write("\n")
            for i in range(0, _round):
                f.write("%d\t" % i)
                for monitor in _KEY_EVENTS_IN_CHROMIUM:
                    for case in _CASES:
                        for task_type in _TASK_TYPE:
                            cpu = self.data[monitor][case][task_type][_CPU_CYCLE][i]
                            time = self.data[monitor][case][task_type][_TIME_IN_US][i]
                            f.write("%f\t%f\t" % (cpu, time))
                f.write("\n")

    def Merge(self):
        _results = self.Alloc()
        for monitor in _KEY_EVENTS_IN_CHROMIUM:
            for case in _CASES:
                for task_type in _TASK_TYPE:
                    for k in [_CPU_CYCLE, _TIME_IN_US]:
                        d = self.data[monitor][case][task_type][k]
                        _results[monitor][case][task_type][k] = np.mean(d)
        self.data = _results

    def RecordFinalResult(self):
        _round = 0
        for case in _CASES:
            if _round == 0:
                _round = self.round[case]
            elif _round != self.round[case]:
                raise Exception("Bad round")

        with open(self.output_file, 'a') as f:
            s = "%s\n#\tFinal Result\n%s\n\n" % ('#'*100, '#'*100)

            s += "monitor\t%s\t\t\t%s\n" % (_CPU_CYCLE, _TIME_IN_US)
            for monitor in _KEY_EVENTS_IN_CHROMIUM:
                s += "%s\t" % monitor
                for k in [_CPU_CYCLE, _TIME_IN_US]:
                    d_baseline = self.data[monitor][_CASE_BASELINE][_TASK_NORMAL][k]
                    d_ours_normal = self.data[monitor][_CASE_OURS][_TASK_NORMAL][k]
                    d_ours_risky = self.data[monitor][_CASE_OURS][_TASK_RISKY][k]
                    if monitor in _SECURITY_MONITOR_TYPE_IN_CHROMIUM:
                        s += "%f\t%f(%f\\%%)\t%f(%f\\%%)\t" % (d_baseline, d_ours_normal,
                                                             (d_ours_normal/d_baseline-1)*100,
                                                             d_ours_risky,
                                                             (d_ours_risky/d_baseline-1)*100)
                    else:
                        s += "NaN\t%f\t%f(%f\\%%)\t" % (d_ours_normal, d_ours_risky,
                                                        (d_ours_risky/d_ours_normal-1)*100)
                s += "\n"
            f.write(s)
            print(s)
