# coding = utf-8


import os
from benchmark.thirdScripts.top10.globalDefinition import NORMAL, TIM, IN_SITES


class ParseLog(object):
    def __init__(self, filepath, site):
        self.filepath = filepath

        # features
        self._features_time = '"%s: ' % site

        self.results = []

    def parse(self):
        # print(">>> Handle %s" % self.filepath)

        with open(self.filepath, "r", encoding="ISO-8859-1") as f:
            content = f.readlines()

            for line in content:
                line = line.strip("\n")

                if self._features_time in line:
                    _, _, remain = line.partition(self._features_time)
                    # print(remain)
                    info = remain.split('''ms", source: ''')
                    # print(info)
                    self.results.append(float(info[0]))

            f.close()

    def run(self):
        self.parse()


class Parse(object):
    def __init__(self):
        _dir = os.path.abspath(os.path.dirname(__file__))
        self._results_tree_dir = os.path.join(_dir, "results")

        self.all_results = {}
        self.final_results = {}

    def run(self):
        if not os.path.exists(self._results_tree_dir):
            raise Exception("%s does not exist" % self._results_tree_dir)

        for site in IN_SITES.keys():
            dirpath_normal = os.path.join(self._results_tree_dir, "results-"+site+"-"+NORMAL)
            dirpath_tim = os.path.join(self._results_tree_dir, "results-" + site + "-" + TIM)
            if not os.path.exists(dirpath_normal):
                continue

            dirpath = {NORMAL: dirpath_normal, TIM: dirpath_tim}

            self.all_results[site] = {NORMAL: [], TIM: []}

            for k in dirpath.keys():
                target_path = dirpath[k]
                files = os.listdir(target_path)
                for file in files:
                    if file.startswith("test"):
                        continue

                    filepath = os.path.join(target_path, file)
                    p = ParseLog(filepath, site=site)
                    p.run()
                    self.all_results[site][k] += p.results

            print("%s\t%s\t%s" % (site, NORMAL, TIM))
            for i in range(0, len(self.all_results[site][NORMAL])):
                print("%d\t%f\t%f" % (i, self.all_results[site][NORMAL][i], self.all_results[site][TIM][i]))
            sum_value_normal, sum_value_tim = 0, 0
            for v in self.all_results[site][NORMAL]:
                sum_value_normal += v
            for v in self.all_results[site][TIM]:
                sum_value_tim += v
            sum_value_normal /= len(self.all_results[site][NORMAL])
            sum_value_tim /= len(self.all_results[site][TIM])
            print("\toverhead-site: ", site, sum_value_normal, sum_value_tim, sum_value_tim/sum_value_normal)


def run():
    Parse().run()
