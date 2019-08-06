# coding = utf-8


import os


_key_for_record_task = "recordTask"
_key_for_switch_task = "switchTask"
_key_for_call_record = "callRecord"
_key_for_original_sop = "originalSOP"
_key_for_tim_sop = "timSOP"

_key_for_cpu_cycle = "cpuCycle"
_key_for_time_usage = "timeUsage"
_key_for_frame_chain_len = "frameChainLen"


class ParseLog(object):
    def __init__(self, filepath):
        self.filepath = filepath

        # features
        self._features_record_task = '>>> [RDTSC] CPU cycles for Switcher::doRecord is: '
        self._features_switch_task = '>>> [RDTSC] CPU cycles for Switcher::doSwitch is: '
        self._features_call_record = ">>> [RDTSC] [CPU cycles for BindingSecurity::CallRecord, " \
                                     "length of frame chain, time] = "
        self._features_tim_sop_check = ">>> [RDTSC] [frame chain's length, CPU cycles for TIM's SOP CHECK] = "
        self._features_original_sop_check = ">>> [RDTSC] CPU cycles for original CHECK is: "

        self.record_tasks = []
        self.switch_tasks = []
        self.call_records = []
        self.original_sop = []
        self.tim_sop = []

        self.results = {}

    def computeWithoutFrameChainLen(self, tasks, key):
        avg_cpu, avg_time = 0.0, 0.0
        for d in tasks:
            avg_cpu += d[_key_for_cpu_cycle]
            avg_time += d[_key_for_time_usage]

        self.results[key] = {
            _key_for_cpu_cycle: avg_cpu/len(tasks),
            _key_for_time_usage: avg_time/len(tasks)
        }

    def computeWithFrameChainLen(self, tasks, key):
        avg_cpu, avg_time, cnt = {}, {}, {}
        for i in range(0, 100):
            avg_cpu[i], avg_time[i], cnt[i] = 0.0, 0.0, 0

        for d in tasks:
            avg_cpu[d[_key_for_frame_chain_len]] += d[_key_for_cpu_cycle]
            avg_time[d[_key_for_frame_chain_len]] += d[_key_for_time_usage]
            cnt[d[_key_for_frame_chain_len]] += 1

        results = {}
        for i in range(0, 100):
            if cnt[i] == 0:
                continue
            results[i] = {
                _key_for_cpu_cycle: avg_cpu[i] / cnt[i],
                _key_for_time_usage: avg_time[i] / cnt[i]
            }
        self.results[key] = results

    def compute(self):
        # 1. for recording tasks
        self.computeWithoutFrameChainLen(self.record_tasks, _key_for_record_task)
        # 2. for switching tasks
        self.computeWithoutFrameChainLen(self.switch_tasks, _key_for_switch_task)
        # 3. for original_sop
        self.computeWithoutFrameChainLen(self.original_sop, _key_for_original_sop)
        # 4. for call record
        self.computeWithFrameChainLen(self.call_records, _key_for_call_record)
        # 5. for tim sop
        self.computeWithFrameChainLen(self.tim_sop, _key_for_tim_sop)

    def parse(self):
        print(">>> Handle %s" % self.filepath)

        with open(self.filepath, "r", encoding="ISO-8859-1") as f:
            content = f.readlines()

            for line in content:
                line = line.strip("\n")

                if self._features_record_task in line:
                    _, _, remain = line.partition(self._features_record_task)
                    info = remain.strip(" ").strip("s").split(", ")
                    data = {_key_for_cpu_cycle: float(info[0]), _key_for_time_usage: float(info[1])}
                    self.record_tasks.append(data)

                elif self._features_switch_task in line:
                    _, _, remain = line.partition(self._features_switch_task)
                    info = remain.strip(" ").strip("s").split(", ")
                    data = {_key_for_cpu_cycle: float(info[0]), _key_for_time_usage: float(info[1])}
                    self.switch_tasks.append(data)

                elif self._features_call_record in line:
                    _, _, remain = line.partition(self._features_call_record)
                    info = remain.strip(" ").strip("s").split(", ")
                    data = {_key_for_cpu_cycle: float(info[0]),
                            _key_for_time_usage: float(info[2]),
                            _key_for_frame_chain_len: 99 if float(info[1]) == 100 else float(info[1])
                            }
                    self.call_records.append(data)

                elif self._features_original_sop_check in line:
                    _, _, remain = line.partition(self._features_original_sop_check)
                    info = remain.strip(" ").strip("s").split(", ")
                    data = {_key_for_cpu_cycle: float(info[0]), _key_for_time_usage: float(info[1])}
                    self.original_sop.append(data)

                elif self._features_tim_sop_check in line:
                    _, _, remain = line.partition(self._features_tim_sop_check)
                    info = remain.strip(" ").strip("s").split(", ")
                    data = {_key_for_cpu_cycle: float(info[1]),
                            _key_for_time_usage: float(info[2]),
                            _key_for_frame_chain_len: 99 if float(info[0]) == 100 else float(info[0])
                            }
                    self.tim_sop.append(data)

            f.close()

    def run(self):
        self.parse()
        self.compute()


class Parse(object):
    def __init__(self):
        _dir = os.path.abspath(os.path.dirname(__file__))
        self._results_dir = os.path.join(_dir, "results")

        self.all_results = []
        self.final_results = {}

    def computeWithoutFrameChainLen(self, results_list, key):
        avg_cpu, avg_time = 0.0, 0.0
        for result in results_list:
            d = result[key]
            avg_cpu += d[_key_for_cpu_cycle]
            avg_time += d[_key_for_time_usage]

        self.final_results[key] = {
            _key_for_cpu_cycle: avg_cpu/len(results_list),
            _key_for_time_usage: avg_time/len(results_list)
        }

    def computeWithFrameChainLen(self, results_list, key):
        avg_cpu, avg_time, cnt = {}, {}, {}
        for i in range(0, 100):
            avg_cpu[i], avg_time[i], cnt[i] = 0.0, 0.0, 0

        for result in results_list:
            for frame_chain_len, d in result[key].items():
                avg_cpu[frame_chain_len] += d[_key_for_cpu_cycle]
                avg_time[frame_chain_len] += d[_key_for_time_usage]
                cnt[frame_chain_len] += 1

        results = {}
        for i in range(0, 100):
            if cnt[i] == 0:
                continue
            results[i] = {
                _key_for_cpu_cycle: avg_cpu[i] / cnt[i],
                _key_for_time_usage: avg_time[i] / cnt[i]
            }
        self.final_results[key] = results

    def run(self):
        if not os.path.exists(self._results_dir):
            raise Exception("%s does not exist" % self._results_dir)

        files = os.listdir(self._results_dir)
        for file in files:
            if file.startswith("test"):
                continue

            filepath = os.path.join(self._results_dir, file)
            p = ParseLog(filepath)
            p.run()

            self.all_results.append(p.results)

        # compute the average value
        self.computeWithoutFrameChainLen(self.all_results, _key_for_record_task)
        self.computeWithoutFrameChainLen(self.all_results, _key_for_switch_task)
        self.computeWithoutFrameChainLen(self.all_results, _key_for_original_sop)
        self.computeWithFrameChainLen(self.all_results, _key_for_tim_sop)
        self.computeWithFrameChainLen(self.all_results, _key_for_call_record)

        print(self.final_results)


def run():
    Parse().run()
