# coding=utf-8

import numpy as np

_invoke_log_file = "invoke.log"
_load_log_file = "load.log"


class Parse(object):
    def __init__(self, filepath):
        self.filepath = filepath

        self._feature_sync64k = '''] "Sync64k+'''
        self._feature_sync512k = '''] "Sync512k+'''
        self._feature_sync1M = '''] "Sync1M+'''
        self._feature_async64k = '''] "Async64k+'''
        self._feature_async512k = '''] "Async512k+'''
        self._feature_async1M = '''] "Async1M+'''

        self._remain_sep = '''ms", '''
        self._time_sep = ''': '''

        self.results = {
            self._feature_sync64k: [],
            self._feature_sync512k: [],
            self._feature_sync1M: [],
            self._feature_async64k: [],
            self._feature_async512k: [],
            self._feature_async1M: []
        }

    def parse(self):
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
        print(">>>>>>>>>> Raw Data")
        for feature in self.results.keys():
            f = feature.replace('''] "''', '').replace('+', '')\
                .replace('Sync', 'Sync (').replace('Async', 'Async (') + ')'
            print(f)
            for d in self.results[feature]:
                print(d, end='\t')
            print("\n")
            average_values[f] = np.mean(self.results[feature])

        return average_values

def parseLoad():
    return Parse(_load_log_file).parse()


def parseInvoke():
    return Parse(_invoke_log_file).parse()

def draw(invokeResults, loadResults):
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mtick

    # 1. read data
    x_label = np.array(["Function Call", "Load Script"])
    bars = ['Sync (64k)', 'Async (64k)', 'Sync (512k)', 'Async (512k)', 'Sync (1M)', 'Async (1M)']
    y = []
    for bar in bars:
        y.append(np.array([invokeResults[bar], loadResults[bar]]))

    print("", "64k", "512k", "1M")
    print("Function Call")
    print("\tLatency", (y[1][0] - y[0][0]), (y[3][0] - y[2][0]), (y[5][0] - y[4][0]))
    print("\tPercentage", (y[1][0] / y[0][0]), (y[3][0] / y[2][0]), (y[5][0] / y[4][0]))
    print("Load Script")
    print("\tLatency", (y[1][1] - y[0][1]), (y[3][1] - y[2][1]), (y[5][1] - y[4][1]))
    print("\tPercentage", (y[1][1] / y[0][1]), (y[3][1] / y[2][1]), (y[5][1] / y[4][1]))

    x = list(range(len(x_label)))
    total_width, n = 0.8, 6
    width = total_width / n

    hatch = ['//', '\\\\']

    plt.figure()
    plt.bar(x, y[0], width=width, label=bars[0], facecolor='white', edgecolor='black')
    for i in range(0, len(x)):
        x[i] += width
    plt.bar(x, y[1], width=width, label=bars[1], facecolor='gray', edgecolor='black')
    for i in range(0, len(x)):
        x[i] += width
    plt.bar(x, y[2], width=width, label=bars[2], facecolor='white', hatch=hatch[0], edgecolor='black')
    for i in range(0, len(x)):
        x[i] += width
    plt.bar(x, y[3], width=width, label=bars[3], facecolor='gray', hatch=hatch[0], edgecolor='black')
    for i in range(0, len(x)):
        x[i] += width
    plt.bar(x, y[4], width=width, label=bars[4], facecolor='white', hatch=hatch[1], edgecolor='black')
    for i in range(0, len(x)):
        x[i] += width
    plt.bar(x, y[5], width=width, label=bars[5], facecolor='gray', hatch=hatch[1], edgecolor='black')

    for i in range(len(x)):
        x[i] = x[i] - width * 3
    plt.xticks(x, x_label)

    # plt.ylim(0, 4500)
    plt.tick_params(labelsize=18)
    plt.ylabel('Time usage (ms)', fontproperties='SimHei', fontsize=18)
    plt.grid(axis="y")
    plt.legend(fontsize=15)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    print("##############################################")
    print("##########   Invoke  #########################")
    print("##############################################")
    invokeResults = parseInvoke()

    print("##############################################")
    print("##########   Invoke  #########################")
    print("##############################################")
    loadResults = parseLoad()

    print(">>>>>>>>> Average Value For Invocation")
    for k, d in invokeResults.items():
        print("%s\t%f" % (k, d))
    print(">>>>>>>>> Average Value For Load")
    for k, d in loadResults.items():
        print("%s\t%f" % (k, d))

    draw(invokeResults, loadResults)
