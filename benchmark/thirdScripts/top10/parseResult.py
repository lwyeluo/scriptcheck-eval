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
        print(">>> Handle %s" % self.filepath)

        with open(self.filepath, "r", encoding="ISO-8859-1") as f:
            content = f.readlines()

            for line in content:
                line = line.strip("\n")

                if self._features_time in line:
                    _, _, remain = line.partition(self._features_time)
                    # print(remain)
                    info = remain.split('''", source: ''')
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

        self._results_data_filepath = os.path.join(_dir, "experiement_data")

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
        self.str_top10_cost_ = "" # write the final average cost into the file |self._results_data_filepath|

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
                    print(p.results)
                    if len(p.results) == 0:
                        continue
                    self.all_results[site][k] += p.results

            print("%s\t%s\t%s" % (site, NORMAL, TIM))
            valid_round = len(self.all_results[site][NORMAL])
            if len(self.all_results[site][NORMAL]) > len(self.all_results[site][TIM]):
                valid_round = len(self.all_results[site][TIM])
            for i in range(0, valid_round):
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

    def recordData(self):
        with open(self._results_data_filepath, 'w') as f:
            round = 0
            sites = [site.replace(".", "").lower() for site in self.top10_libraries_]
            data = ""
            for site in sites:
                if round < len(self.all_results[site][NORMAL]):
                    round = len(self.all_results[site][NORMAL])
                data += "\t%s-NORMAL\t%s-TIM" % (site, site)
            f.write(data + "\n")
            for i in range(0, round):
                data = "%d" % i
                for site in sites:
                    if i >= len(self.all_results[site][NORMAL]):
                        data += "\t-\t-"
                    else:
                        data += "\t%f\t%f" % (self.all_results[site][NORMAL][i], self.all_results[site][TIM][i])
                f.write(data + "\n")

    def printAndRecord(self, data, end="\n"):
        self.str_top10_cost_ += data + end
        print(data, end=end)

    def writeDataIntoFile(self):
        with open(self._results_data_filepath, 'a') as f:
            f.write("\n\n")
            f.write(self.str_top10_cost_)

    def printf(self):
        for i in range(0, 3):
            print("********************************************************")
        cnt = 0
        average_cost = 0.0
        while True:
            idx = cnt+5 if cnt+5 <= len(self.top10_libraries_) else len(self.top10_libraries_)
            sites = [self.top10_libraries_[i] for i in range(cnt, idx)]
            for site in sites:
                self.printAndRecord("\t&\t\\textbf{%s}" % site, end="")
            self.printAndRecord(" \\\\ \\hline")
            self.printAndRecord("Baseline", end="")
            for site in sites:
                self.printAndRecord("\t&\t%s" % self.top10_cost_[site.replace(".", "").lower()][NORMAL], end="")
            self.printAndRecord(" \\\\ \\hline")
            self.printAndRecord("Ours", end="")
            for site in sites:
                o = self.top10_cost_[site.replace(".", "").lower()][NORMAL]
                n = self.top10_cost_[site.replace(".", "").lower()][TIM]
                cost = (float(n)/float(o) - 1) * 100
                average_cost += float("%.3f" % cost)
                self.printAndRecord("\t&\t%s" % n, end="")
                self.printAndRecord(" (%.3f\\%%)" % cost, end="")
            self.printAndRecord(" \\\\ \\hline")
            cnt += 5
            if cnt >= len(self.top10_libraries_):
                break
        self.printAndRecord("The cost on average is %f" % (average_cost/len(self.top10_libraries_)))
        self.writeDataIntoFile()


def run():
    p = Parse()
    p.run()
    p.recordData()
    p.printf()


if __name__ == '__main__':
    run()
