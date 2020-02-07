# coding = utf-8


import os
from benchmark.thirdScripts.top10.globalDefinition import NORMAL, TIM, IN_SITES


class ParseLog(object):
    def __init__(self, filepath, site):
        self.filepath = filepath

        # features
        self._features_time = '"%s: ' % site
        self._features_disallow_form = "the current task cannot access the specified element"

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
                elif self._features_disallow_form in line:
                    print(line)

            f.close()

    def run(self):
        self.parse()


class Parse(object):
    def __init__(self):
        _dir = os.path.abspath(os.path.dirname(__file__))
        self._results_tree_dir = os.path.join(_dir, "results")

        self.all_results = {}
        self.final_results = {}

        self.top10_libraries_ = [
            "Chart.js",
            "Highcharts",
            "particles.js",
            "Raphael",
            "D3",
            "three.js",
            "MathJax",
            "AmCharts",
            "Supersized",
            "GoogleCharts"
        ]

        self.top10_cost_ = {}

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

            self.top10_cost_[site] = {
                NORMAL: "%.3f" % sum_value_normal,
                TIM: "%.3f" % sum_value_tim
            }

    def printf(self):
        for i in range(0, 3):
            print("********************************************************")
        cnt = 0
        average_cost = 0.0
        while True:
            sites = [self.top10_libraries_[i] for i in range(cnt, cnt+5)]
            for site in sites:
                print("\t&\t\\textbf{%s}" % site, end="")
            print(" \\\\ \\hline")
            print("Baseline", end="")
            for site in sites:
                print("\t&\t%s" % self.top10_cost_[site.replace(".", "").lower()][NORMAL], end="")
            print(" \\\\ \\hline")
            print("Ours", end="")
            for site in sites:
                o = self.top10_cost_[site.replace(".", "").lower()][NORMAL]
                n = self.top10_cost_[site.replace(".", "").lower()][TIM]
                cost = (float(n)/float(o) - 1) * 100
                average_cost += cost
                print("\t&\t%s" % n, end="")
                print(" (%.2f\\%%)" % cost, end="")
            print(" \\\\ \\hline")
            cnt += 5
            if cnt == 10:
                break
        print("The cost on average is", average_cost/10)



def run():
    p = Parse()
    p.run()
    p.printf()


if __name__ == '__main__':
    run()
