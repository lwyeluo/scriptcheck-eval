# coding=utf-8

import json
import os
import codecs
import numpy as np
from benchmark.thirdScripts.dromaeo.globalDefinition import _CASES, _CASE_BASELINE, _CASE_OURS, _COST

_NORMAL_ = _CASE_BASELINE
_TIM_ = _CASE_OURS

class Parser(object):
    def __init__(self):
        self.benchmarkNames = [
            "DOM Core Tests",
            "DOM Attributes",
            "DOM Modification",
            "DOM Query",
            "DOM Traversal"
        ]

        _dir = os.path.dirname(os.path.abspath(__file__))
        self._results_normal_filepath = os.path.join(_dir, "dromaeo_node_results_" + _NORMAL_)
        self._results_tim_filepath = os.path.join(_dir, "dromaeo_node_results_" + _TIM_)

        self._results_data_filepath = os.path.join(_dir, "experiement_data")
        self.str_cost_ = ""  # used to record the cost (in String)
        self.results_cost_ = {}  # used to record the cost (in Dict)


    def parse(self, filepath):
        round = 0
        results = []
        with open(filepath, "r") as f:
            line = f.readline()
            print(line.strip("\n"))
            while line:
                # find for a new round
                while line.find(">>>") != 0:
                    continue
                round += 1
                results.append({})

                print("!!! A new round -> ", line.strip("\n"))
                line = f.readline()
                # collect the data for this round
                while line and line.find(">>>") != 0:
                    for benchmark in self.benchmarkNames:
                        if benchmark in line:
                            while True:
                                line = f.readline()
                                if line.find("runs/s") != -1:
                                    break
                            n, _, r = line.partition("runs/s")
                            # strip the header when the data is a digit
                            d_, i_ = n, len(n)
                            for i in range(0, i_):
                                if not d_[i].isdigit():
                                    continue
                                else:
                                    d_ = d_[i:]
                                    break
                            print(n, d_)
                            # save the results
                            results[round - 1][benchmark] = d_
                            print(line.strip("\n"), "\t\t\t>>>>", benchmark, n)
                    # read the next line
                    line = f.readline()
            print("end")
        return results

    def printAndRecord(self, data, end="\n"):
        self.str_cost_ += data + end
        print(data, end=end)

    def writeDataIntoFile(self):
        with open(self._results_data_filepath, 'a') as f:
            f.write("\n\n")
            f.write(self.str_cost_)

    def run(self):
        # parse the results
        results_normal = self.parse(self._results_normal_filepath)
        results_tim = self.parse(self._results_tim_filepath)

        if len(results_normal) != len(results_tim):
            raise Exception("The round of NORMAL (%d) and TIM (%d) is not equal" % (
                len(results_normal), len(results_tim)
            ))

        # to calculate the average value
        results_average = {}
        for benchmark in self.benchmarkNames:
            results_average[benchmark] = {_NORMAL_: 0, _TIM_: 0}

        with open(self._results_data_filepath, "w") as f: # to save the benchmark results
            # record the raw data into file
            for benchmark in self.benchmarkNames:
                f.write("\t%s-%s" % (benchmark, _NORMAL_))
            for benchmark in self.benchmarkNames:
                f.write("\t%s-%s" % (benchmark, _TIM_))
            f.write("\n")

            for i in range(0, len(results_normal)):
                f.write("%s" % str(i))
                for benchmark in self.benchmarkNames:
                    usage = float(results_normal[i][benchmark].replace("ms", ""))
                    results_average[benchmark][_NORMAL_] += usage
                    f.write("\t" + str(usage))
                for benchmark in self.benchmarkNames:
                    usage = float(results_tim[i][benchmark].replace("ms", ""))
                    results_average[benchmark][_TIM_] += usage
                    f.write("\t" + str(usage))
                f.write("\n")

        # calculate the average value
        for benchmark in self.benchmarkNames:
            d1, d2 = results_average[benchmark][_NORMAL_], results_average[benchmark][_TIM_]
            v1, v2 = d1 / len(results_normal), d2 / len(results_tim)
            self.results_cost_[benchmark] = {_NORMAL_: v1, _TIM_: v2, _COST: v2/v1}

        # print the cost
        self.printf()

    def printf(self):
        # print the final
        for benchmark in self.benchmarkNames:
            self.printAndRecord("\t&\t\\textbf{%s}" % benchmark, end="")
        self.printAndRecord(" \\\\ \\hline")

        self.printAndRecord("Baseline", end="")
        for benchmark in self.benchmarkNames:
            self.printAndRecord("\t&\t%f" % self.results_cost_[benchmark][_NORMAL_], end="")
        self.printAndRecord(" \\\\ \\hline")

        self.printAndRecord("Ours", end="")
        for benchmark in self.benchmarkNames:
            self.printAndRecord("\t&\t%f" % self.results_cost_[benchmark][_TIM_], end="")
            self.printAndRecord(" (%.3f\\%%)" % ((1-self.results_cost_[benchmark][_COST])*100), end="")
        self.printAndRecord(" \\\\ \\hline")

        self.writeDataIntoFile()


def run():
    Parser().run()