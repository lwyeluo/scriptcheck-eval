# coding=utf-8

import os
import numpy as np
from benchmark.thirdScripts.speedometer.globalDefinition import _CASES, _CASE_BASELINE, _CASE_OURS

class Parse(object):

    def __init__(self):
        self._dir = os.path.abspath(os.path.dirname(__file__))

        self._feature = "DONE FOR RUNNING Speedometer. Result is "

        self._raw_results = {}
        self._results_filepath = os.path.join(self._dir, "experiement_data")

        self._round = 0

    def parse(self):
        _round = {}
        for case in _CASES:
            self._raw_results[case] = []
            _round[case] = 0

            filepath = os.path.join(self._dir, "speedometer_node_results_%s" % case)

            with open(filepath, 'r') as f:
                for line in f.readlines():
                    if self._feature in line:
                        _, _, d = line.partition(self._feature)
                        v = d.strip("\n").strip(" ")
                        self._raw_results[case].append(float(v))
                        _round[case] += 1

        self._round = 0
        for case in _CASES:
            if self._round == 0:
                self._round = _round[case]
            elif self._round != _round[case]:
                raise Exception("The cases have different round. %d vs. %d" % (self._round, _round[case]))

    def writeRawDataIntoFile(self):
        with open(self._results_filepath, 'w') as f:
            for case in _CASES:
                f.write("\t%s" % case)
            f.write("\n")

            for i in range(0, self._round):
                f.write("%d" % i)
                for case in _CASES:
                    f.write("\t%f" % self._raw_results[case][i])
                f.write("\n")

            # average value
            average_value = {}
            for case in _CASES:
                average_value[case] = np.mean(self._raw_results[case])
            cost = 1 - average_value[_CASE_OURS] / average_value[_CASE_BASELINE]
            _out = "COST: %f %f(%f%%)" % (average_value[_CASE_BASELINE], average_value[_CASE_OURS], cost*100)
            print(_out)
            f.write(_out)

    def run(self):
        self.parse()
        self.writeRawDataIntoFile()


def run():
    print("[SPEEDOMETER] >>> parse the results")
    Parse().run()
