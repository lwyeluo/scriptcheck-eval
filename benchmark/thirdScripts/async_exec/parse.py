# coding=utf-8

import numpy as np
import os


class Features(object):

    _data_size = "512k"

    _feature_async512k_all = '''] "all-Async%s+''' % _data_size
    _feature_async512k_create0 = '''] "create0-Async%s+''' % _data_size
    _feature_async512k_create1 = '''] "create1-Async%s+''' % _data_size
    _feature_async512k_wait0 = '''] "wait0-Async%s+''' % _data_size
    _feature_async512k_wait1 = '''] "wait1-Async%s+''' % _data_size
    _feature_async512k_func = '''] "func-Async%s+''' % _data_size


class ParseLog(object):
    def __init__(self, filepath):
        self.filepath = filepath

        # self._remain_sep = '''ms", '''
        self._remain_sep = '''", source'''
        self._time_sep = ''': '''

        self.results = {
            Features._feature_async512k_all: [],
            Features._feature_async512k_create0: [],
            Features._feature_async512k_create1: [],
            Features._feature_async512k_wait0: [],
            Features._feature_async512k_wait1: [],
            Features._feature_async512k_func: [],
        }

    def run(self):
        print(">>> Handle ", self.filepath)
        with open(self.filepath, "r", encoding="ISO-8859-1") as f:
            content = f.readlines()

            for line in content:
                line = line.strip("\n")

                for feature in self.results.keys():
                    if feature in line:
                        _, _, r = line.partition(feature)
                        d, _, _ = r.partition(self._remain_sep)
                        _, _, t = d.partition(self._time_sep)
                        self.results[feature].append(float(t))

        average_values = {}
        # print(">>>>>>>>>> Raw Data")
        for feature in self.results.keys():
            f = feature.replace('''] "''', '').replace('+', '')\
                .replace('Sync', 'Sync (').replace('Async', 'Async (') + ')'
            # print(f, end="\t")
            # for d in self.results[feature]:
            #     print(d, end='\t')
            # print("\n")
            average_values[f] = np.mean(self.results[feature])
            print("\t\t%s\t%.3f" % (f, average_values[f]))

        return average_values

class Parse(object):
    def __init__(self):
        _dir = os.path.abspath(os.path.dirname(__file__))
        self._results_tree_dir = os.path.join(_dir, "results")

        self._results_data_filepath = os.path.join(_dir, "experiement_data")

        self.str_cost_ = ""  # used to record the cost (in String)
        self.round = 0

        self._results_array = {}
        self._results = {}

    def run(self):
        if not os.path.exists(self._results_tree_dir):
            raise Exception("%s does not exist" % self._results_tree_dir)
        files = os.listdir(self._results_tree_dir)

        self.round = len(files)-1

        for file in files:
            if file.startswith("test"):
                continue
            filepath = os.path.join(self._results_tree_dir, file)
            p = ParseLog(filepath)
            results = p.run()
            for r in results.keys():
                if r not in self._results_array.keys():
                    self._results_array[r] = [float(results[r])]
                else:
                    self._results_array[r].append(float(results[r]))

        for r in self._results_array.keys():
            # print(self._results_array[r])
            self._results[r] = np.mean(self._results_array[r])

        return self._results

    def writeRawDataIntoFile(self):
        with open(self._results_data_filepath, "w") as f:  # to save the benchmark results

            # print the raw data
            tags = [r for r in self._results_array.keys()]
            for t in tags:
                f.write("\t%s" % t)
            f.write("\n")
            for i in range(0, self.round):
                f.write("%d" % i)
                for t in tags:
                    f.write("\t%f" % self._results_array[t][i])
                f.write("\n")
            f.write("\n\n\n")

    def printAndRecord(self, data, end="\n"):
        self.str_cost_ += data + end
        print(data, end=end)

    def writeDataIntoFile(self):
        with open(self._results_data_filepath, 'a') as f:
            f.write("\n\n")
            f.write(self.str_cost_)

    def convertLabel(self, feature):
        return feature.replace('''] "''', '').replace('+', '')\
                .replace('Sync', 'Sync (').replace('Async', 'Async (') + ')'

    def printf(self):
        self.printAndRecord(">>>>>>>>> Average Value For Invocation")
        for k, d in self._results.items():
            self.printAndRecord("%s\t%f" % (k, d))

        self.printAndRecord(">>>>>>>>> Final Results")
        self.printAndRecord("\\textbf{Total Overhead}\t&\t\\textbf{Task Creation}\t&\t\\text{Waiting Time}\t&\tfunction invocation")

        label_create0 = self.convertLabel(Features._feature_async512k_create0)
        label_create1 = self.convertLabel(Features._feature_async512k_create1)
        label_wait0 = self.convertLabel(Features._feature_async512k_wait0)
        label_wait1 = self.convertLabel(Features._feature_async512k_wait1)
        label_func = self.convertLabel(Features._feature_async512k_func)
        label_all = self.convertLabel(Features._feature_async512k_all)

        cost_create0 = "%.3f" % self._results[label_create0]
        cost_create1 = "%.3f" % self._results[label_create1]
        cost_wait0 = "%.3f" % self._results[label_wait0]
        cost_wait1 = "%.3f" % self._results[label_wait1]
        # cost_func_remain = "%.3f" % (float(cost_all) - float(cost_create0) - float(cost_wait0)
        #             - float(cost_create1) - float(cost_wait1))
        cost_func = "%.3f" % float(self._results[label_func])
        cost = float(cost_create0) + float(cost_create1) + float(cost_wait0) + float(cost_wait1)
        cost_all = cost + float(cost_func)
        cost_async = "%.3f" % self._results[label_all]
        self.printAndRecord("%.3f/%s\t&\t%f(%s+%s)\t&\t%f(%s+%s)\t&\t" %
                            (cost, cost_async,
                             float(cost_create0) + float(cost_create1), cost_create0, cost_create1,
                             float(cost_wait0) + float(cost_wait1), cost_wait0, cost_wait1))

        print("cost:\t%.3f" % (cost/cost_all*100))
        print("waiting: %f\t%s\t%s" % (float(cost_wait0) + float(cost_wait1), cost_wait0, cost_wait1))

        self.writeDataIntoFile()

def parseInvoke():
    p = Parse()
    p.run()
    p.writeRawDataIntoFile()
    p.printf()

def run():
    parseInvoke()

if __name__ == '__main__':
    run()