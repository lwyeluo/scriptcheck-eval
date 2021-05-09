# coding=utf-8

import os
import numpy as np
from benchmark.thirdScripts.library.globalDefinition import _CASES, _CASE_BASELINE, _CASE_OURS, IN_SITES

class Parse(object):

    def __init__(self):
        _dir = os.path.abspath(os.path.dirname(__file__))
        self._dir = os.path.join(_dir, "results")

        self._feature = '''DONE FOR RUNNING 3RD LIBRARY. TIME USAGE is '''

        self._raw_results = {}
        self._results_filepath = os.path.join(_dir, "experiement_data")

        self.top10_cost_ = {}
        self.str_top10_cost_ = ""  # write the final average cost into the file |self._results_filepath|

        self._sites = IN_SITES

        self._round = 0

    def parse(self):
        for site in self._sites:
            self._raw_results[site] = {}

            for case in _CASES:
                self._raw_results[site][case] = []

                filepath = os.path.join(self._dir, "%s_node_results_%s" % (site, case))

                round = 0

                with open(filepath, 'r') as f:
                    for line in f.readlines():
                        if self._feature in line:
                            _, _, d = line.partition(self._feature)
                            v = d.strip("\n").strip(" ")
                            print(line, v)
                            self._raw_results[site][case].append(float(v))
                            round += 1

                # check round
                if self._round == 0:
                    self._round = round
                elif self._round != round:
                    raise Exception("The cases have different round. %d vs. %d" % (self._round, round))

            sum_value_normal, sum_value_tim = 0, 0
            for v in self._raw_results[site][_CASE_BASELINE]:
                sum_value_normal += v
            for v in self._raw_results[site][_CASE_OURS]:
                sum_value_tim += v
            sum_value_normal /= len(self._raw_results[site][_CASE_BASELINE])
            sum_value_tim /= len(self._raw_results[site][_CASE_OURS])
            print("\toverhead-site: ", site, sum_value_normal, sum_value_tim, sum_value_tim / sum_value_normal)

            self.top10_cost_[site] = {
                _CASE_BASELINE: "%.3f" % sum_value_normal,
                _CASE_OURS: "%.3f" % sum_value_tim
            }

    def recordData(self):
        with open(self._results_filepath, 'w') as f:
            data = ""
            for site in self._sites:
                data += "\t%s-%s\t%s-%s" % (site, _CASE_BASELINE, site, _CASE_OURS)
            f.write(data + "\n")
            for i in range(0, self._round):
                data = "%d" % i
                for site in self._sites:
                    if i >= len(self._raw_results[site][_CASE_BASELINE]):
                        data += "\t-\t-"
                    else:
                        data += "\t%f\t%f" % (self._raw_results[site][_CASE_BASELINE][i], self._raw_results[site][_CASE_OURS][i])
                f.write(data + "\n")

    def printAndRecord(self, data, end="\n"):
        self.str_top10_cost_ += data + end
        print(data, end=end)

    def writeDataIntoFile(self):
        with open(self._results_filepath, 'a') as f:
            f.write("\n\n")
            f.write(self.str_top10_cost_)

    def printf(self):
        for i in range(0, 3):
            print("********************************************************")
        cnt = 0
        average_cost = 0.0
        while True:
            idx = cnt + 5 if cnt + 5 <= len(self._sites) else len(self._sites)
            sites = [self._sites[i] for i in range(cnt, idx)]
            for site in sites:
                self.printAndRecord("\t&\t\\textbf{%s}" % site, end="")
            self.printAndRecord(" \\\\ \\hline")
            self.printAndRecord("Baseline", end="")
            for site in sites:
                self.printAndRecord("\t&\t%s" % self.top10_cost_[site.replace(".", "").lower()][_CASE_BASELINE], end="")
            self.printAndRecord(" \\\\ \\hline")
            self.printAndRecord("Ours", end="")
            for site in sites:
                o = self.top10_cost_[site.replace(".", "").lower()][_CASE_BASELINE]
                n = self.top10_cost_[site.replace(".", "").lower()][_CASE_OURS]
                cost = (float(n) / float(o) - 1) * 100
                average_cost += float("%.3f" % cost)
                self.printAndRecord("\t&\t%s" % n, end="")
                self.printAndRecord(" (%.3f\\%%)" % cost, end="")
            self.printAndRecord(" \\\\ \\hline")
            cnt += 5
            if cnt >= len(self._sites):
                break
        self.printAndRecord("The cost on average is %f" % (average_cost / len(self._sites)))
        self.writeDataIntoFile()

    def run(self):
        self.parse()
        self.recordData()
        self.printf()

def run():
    print("[3RD LIBRARY] >>> parse the results")
    Parse().run()
