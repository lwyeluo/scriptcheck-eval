# coding=utf-8

import numpy as np
import os


class ParseLog(object):
    def __init__(self, filepath):
        self.filepath = filepath

        data_size = "512k"

        self._feature_sync512k = '''] "Sync%s+''' % data_size
        self._feature_async512k_all = '''] "all-Async%s+''' % data_size
        self._feature_async512k_create0 = '''] "create0-Async%s+''' % data_size
        self._feature_async512k_create1 = '''] "create1-Async%s+''' % data_size
        self._feature_async512k_wait0 = '''] "wait0-Async%s+''' % data_size
        self._feature_async512k_wait1 = '''] "wait1-Async%s+''' % data_size
        self._feature_async512k_strip = '''] "strip-Async%s+''' % data_size
        self._feature_async512k_func = '''] "func-Async%s+''' % data_size
        self._feature_async512k_ret = '''] "ret-Async%s+''' % data_size

        # self._remain_sep = '''ms", '''
        self._remain_sep = '''", source'''
        self._time_sep = ''': '''

        self.results = {
            self._feature_sync512k: [],
            self._feature_async512k_all: [],
            self._feature_async512k_create0: [],
            self._feature_async512k_create1: [],
            self._feature_async512k_wait0: [],
            self._feature_async512k_wait1: [],
            self._feature_async512k_strip: [],
            self._feature_async512k_func: [],
            self._feature_async512k_ret: []
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
            # print(f)
            # for d in self.results[feature]:
            #     print(d, end='\t')
            # print("\n")
            average_values[f] = np.mean(self.results[feature])

        return average_values

class Parse(object):
    def __init__(self):
        _dir = os.path.abspath(os.path.dirname(__file__))
        self._results_tree_dir = os.path.join(_dir, "results")

        self._results_array = {}
        self._results = {}

    def run(self):
        if not os.path.exists(self._results_tree_dir):
            raise Exception("%s does not exist" % self._results_tree_dir)
        files = os.listdir(self._results_tree_dir)
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


def parseInvoke():
    return Parse().run()

def run():
    # print("##############################################")
    # print("##########   Invoke  #########################")
    # print("##############################################")
    invokeResults = parseInvoke()

    data_size = "512k"
    _label_sync = "Sync (%s)" % data_size
    _label_all_async = "all-Async (%s)" % data_size
    _label_create0_async = "create0-Async (%s)" % data_size
    _label_create1_async = "create1-Async (%s)" % data_size
    _label_wait0_async = "wait0-Async (%s)" % data_size
    _label_wait1_async = "wait1-Async (%s)" % data_size
    _label_func_async = "func-Async (%s)" % data_size
    _label_ret_async = "ret-Async (%s)" % data_size
    _label_strip_async = "strip-Async (%s)" % data_size
    features = {
        _label_sync: 100,
        _label_all_async: 100,
        _label_create0_async: 0.25,
        _label_create1_async: 0.25,
        _label_wait0_async: 2,
        _label_wait1_async: 2,
        _label_func_async: 100,
        _label_ret_async: 100
    }

    print(">>>>>>>>> Average Value For Invocation")
    for k, d in invokeResults.items():
        print("%s\t%f" % (k, d))

    print(">>>>>>>>> Final Results")
    print("all\t&\tcreate task\t&\tfunction invocation\t&\twait")
    # cost_all = "%.3f" % (invokeResults[_label_all_async] - invokeResults[_label_strip_async])
    cost_create0 = "%.3f" % invokeResults[_label_create0_async]
    cost_create1 = "%.3f" % invokeResults[_label_create1_async]
    cost_wait0 = "%.3f" % invokeResults[_label_wait0_async]
    cost_wait1 = "%.3f" % invokeResults[_label_wait1_async]
    # cost_func_remain = "%.3f" % (float(cost_all) - float(cost_create0) - float(cost_wait0)
    #             - float(cost_create1) - float(cost_wait1))
    cost_func = "%.3f" % float(invokeResults[_label_func_async])
    cost = float(cost_create0) + float(cost_create1) + float(cost_wait0) + float(cost_wait1)
    cost_all = cost + float(cost_func)
    cost_async = "%.3f" % invokeResults[_label_all_async]
    print("%.3f/%s\t&\t%s+%s\t&\t%s\t&\t%s+%s\t" % (cost_all, cost_async, cost_create0,
                                                  cost_create1, cost_func,
                                                  cost_wait0, cost_wait1))
    print("%.3f\t&\t%.3f+%.3f\t&\t%.3f\t&\t%.3f+%.3f\t" % (cost_all * 2.7 / 2.9,
                                                 float(cost_create0) * 2.7 / 2.9,
                                                 float(cost_create1) * 2.7 / 2.9,
                                                 float(cost_func) * 2.7 / 2.9,
                                                 float(cost_wait0) * 2.7 / 2.9,
                                                 float(cost_wait1) * 2.7 / 2.9))

if __name__ == '__main__':
    run()