# coding=utf-8


import signal
import os
from threading import Timer
from utils.executor import *

from utils.globalDefinition import _chrome_binary, _node_binary, _timeout, _timeout_for_node
from utils.globalDefinition import _node_filename, _node_run_url_filename
from utils.globalDefinition import _node_run_url_filename_kraken, _node_run_url_filename_dromeao
from utils.globalDefinition import _node_run_url_filename_jetstream2, _node_run_url_filename_speedometer
from utils.globalDefinition import _node_run_url_filename_library
from utils.globalDefinition import _USE_PROXY_, _PROXY_FOR_CHROME_
from run_script.globalDefinition import *


class RunUrl(object):
    def __init__(self, url, ret_filename, node_filename=_node_filename,
                 timeout=_timeout, timeout_for_node=_timeout_for_node,
                 chrome_binary=_chrome_binary):
        self.url = url  # the url to be loaded
        self.ret_filename = ret_filename  # the file path to save the Chrome's log

        self.chrome_binary_ = chrome_binary

        self.node_filename = node_filename
        self.timeout = timeout
        self.timeout_for_node = timeout_for_node
        self.my_timer = ""
        self.timeout_check_crash = 5
        self.timer_check_crash_cnt = 0

        # some features logged by node
        self.features_completed = '''result: { type: 'string', value: 'complete' }'''
        self.features_collect_frame_info = '''>>> Prepare to get frames's information'''
        self.features_frame_info = "**********"
        self.feature_telemetry_error = '''ERROR WHEN RUNNING TELEMETRY'''
        self.feature_telemetry_done = '''DONE FOR RUNNING TELEMETRY'''
        self.feature_jetstream2_done = '''DONE FOR RUNNING JetStream2. Score is'''
        self.feature_speedometer_done = '''DONE FOR RUNNING Speedometer. Result is '''
        self.feature_3rd_library_done = '''DONE FOR RUNNING 3RD LIBRARY. TIME USAGE is '''

        # the information for frames
        self.frame_info = {}  # {'parent': {'url': url, 'domain': domain}, 'frameID': {'url': url, 'domain': domain}}

        # to save some benchmark results
        self._results_for_kraken = ""
        self._results_for_dromeao = ""
        self._results_for_jetsteam2 = ""
        self._results_for_speedometer = ""
        self._results_for_3rd_library = ""

        self.flag = CHROME_RUN_FLAG_SUCCESS
        self.flag = self.run()  # flag refers to definitions in `globalDefinition`

    def timeoutCallback(self, process_node):
        # should close
        self.timer_check_crash_cnt += 1
        if self.timer_check_crash_cnt * self.timeout_check_crash > self.timeout_for_node:
            print("\t\tTimeout! kill....")
            try:
                os.killpg(process_node.pid, signal.SIGKILL)
            except Exception as error:
                print(error)

        # check crash
        cmd = "ps -ef | grep -v grep | grep %s | grep renderer" % self.chrome_binary_
        print("\t\tCheck Crash....", cmd)
        output, status = executeWithoutCheckStatus(cmd)
        print(output, status)
        if output.strip("\n") == "":
            print("\t\tCrash! kill....")
            try:
                os.killpg(process_node.pid, signal.SIGKILL)
            except Exception as error:
                print(error)

            self.flag = CHROME_RUN_FLAG_CRASH
        else:
            self.my_timer.cancel()
            self.my_timer = Timer(self.timeout_check_crash, self.timeoutCallback, [process_node])
            self.my_timer.start()

    # collect the url and domains for all (same-origin) frames
    def collectInformationForFrames(self, logs):
        # print(logs)
        if self.features_collect_frame_info in logs:
            info = logs[logs.find(self.features_collect_frame_info):].strip('\\n').split('\\n')

            for i in range(1, len(info)):
                data = info[i].strip('\\t')
                if self.features_frame_info in data:
                    # parse the information for frame
                    child_info = data.split("\\t")
                    if len(child_info) != 5:
                        print("[ERROR] we failed to parse %s" % data)
                        continue
                    self.frame_info[child_info[1]] = {
                        'url': child_info[2],
                        'domain': child_info[3]
                    }

    # collect the results of kraken benchmark
    def collectResultsForKraken(self, logs):
        feature = "RESULTS (means and 95% confidence intervals)"
        if feature in logs:
            info = logs[logs.find(feature):].strip('\\n').split('\\n')
            self._results_for_kraken = '\n'.join(info)
            return True
        return False

    # collect the results of Dromeao benchmark
    def collectResultsForDromeao(self, logs):
        feature = "DOM Core Tests"
        if feature in logs:
            info = logs[logs.find(feature):].strip('\\n').split('\\n')
            self._results_for_dromeao = '\n'.join(info)
            return True
        return False

    # collect the results of JetStream2 benchmark
    def collectResultsForJetStream2(self, logs):
        feature = self.feature_jetstream2_done
        if feature in logs:
            info = logs[logs.find(feature):].strip('\\n').split('\\n')
            self._results_for_jetsteam2 = '\n'.join(info)

    # collect the results of speedometer benchmark
    def collectResultsForSpeedometer(self, logs):
        feature = self.feature_speedometer_done
        if feature in logs:
            info = logs[logs.find(feature):].strip('\\n').split('\\n')
            self._results_for_speedometer = '\n'.join(info)
            return True
        return False

    # collect the results of 3rd library benchmark
    def collectResultsFor3rdLibrary(self, logs):
        feature = self.feature_3rd_library_done
        if feature in logs:
            info = logs[logs.find(feature):].strip('\\n').split('\\n')
            self._results_for_3rd_library = '\n'.join(info)
            return True
        return False

    def handleNodeLog(self, stdout):
        if self.feature_telemetry_done in str(stdout):
            print("\t\tweb page [%s] is completed!" % self.url)
            flag = CHROME_RUN_FLAG_TELEMETRY_SUCCESS
        elif self.feature_telemetry_error in str(stdout):
            print("\t\tweb page [%s] has error: %s" % (self.url, self.feature_telemetry_error))
            flag = CHROME_RUN_FLAG_TELEMETRY_ERROR
        elif self.feature_jetstream2_done in str(stdout):
            print("\t\tweb page [%s] is completed" % self.url)
            flag = CHROME_RUN_FLAG_JETSTREAM2_SUCCESS
        elif self.feature_3rd_library_done in str(stdout):
            print("\t\tweb page [%s] is completed" % self.url)
            flag = CHROME_RUN_FLAG_3RD_LIBRARY_SUCCESS
        elif self.features_completed in str(stdout):
            print("\t\tweb page [%s] is completed!" % self.url)
            flag = CHROME_RUN_FLAG_SUCCESS
        else:
            # print(str(stdout))
            print("\t\tweb page [%s] is TIMEOUT!" % self.url)
            flag = CHROME_RUN_FLAG_TIMEOUT

        # collect the url and domains for all (same-origin) frames
        if self.node_filename == _node_filename:
            self.collectInformationForFrames(str(stdout))

        # collect the results of some benchmarks
        if self.node_filename == _node_run_url_filename_kraken:
            if self.collectResultsForKraken(str(stdout)):
                flag = CHROME_RUN_FLAG_KRAKEN_SUCCESS
            else:
                flag = CHROME_RUN_FLAG_KRAKEN_ERROR
        elif self.node_filename == _node_run_url_filename_dromeao:
            if self.collectResultsForDromeao(str(stdout)):
                flag = CHROME_RUN_FLAG_DROMAEO_SUCCESS
            else:
                flag = CHROME_RUN_FLAG_DROMAEO_ERROR
        elif self.node_filename == _node_run_url_filename_speedometer:
            if self.collectResultsForSpeedometer(str(stdout)):
                flag = CHROME_RUN_FLAG_SPEEDOMETER_SUCCESS
            else:
                flag = CHROME_RUN_FLAG_SPEEDOMETER_ERROR
        elif self.node_filename == _node_run_url_filename_library:
            if self.collectResultsFor3rdLibrary(str(stdout)):
                flag = CHROME_RUN_FLAG_3RD_LIBRARY_SUCCESS
            else:
                flag = CHROME_RUN_FLAG_3RD_LIBRARY_ERROR
        elif self.node_filename == _node_run_url_filename_jetstream2:
            self.collectResultsForJetStream2(str(stdout))

        return flag

    def run(self):
        flag = 0  # 0: completed, 1: timeout
        ret_fd = open(self.ret_filename, 'w')

        print(self.chrome_binary_)
        cmd = ""
        if _USE_PROXY_:
            cmd = [self.chrome_binary_, '--remote-debugging-port=9222', _PROXY_FOR_CHROME_]
        else:
            cmd = [self.chrome_binary_, '--remote-debugging-port=9222']
        # cmd = [self.chrome_binary_, '--remote-debugging-port=9222']
        process_chrome = subprocess.Popen(cmd, stderr=ret_fd,
                                          stdout=ret_fd)
        print('>>> START ' + self.url)
        time.sleep(5)

        cmd = [_node_binary, self.node_filename, self.url, str(self.timeout_for_node)]
        print(' '.join(cmd))
        process_node = subprocess.Popen(cmd,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, preexec_fn=os.setsid)
        # create a timer
        self.my_timer = Timer(self.timeout_check_crash, self.timeoutCallback, [process_node])
        self.my_timer.start()

        stdout, _ = process_node.communicate()
        print(str(stdout))

        if self.flag != CHROME_RUN_FLAG_CRASH:
            flag = self.handleNodeLog(stdout)
        else:
            flag = CHROME_RUN_FLAG_CRASH

        print('>>> FINISH ' + self.url)

        self.my_timer.cancel()

        time.sleep(2)
        # kill chrome
        try:
            print("\t>>> kill Chrome [%d]" % process_chrome.pid)
            os.kill(process_chrome.pid, signal.SIGKILL)
        # os.killpg(process_chrome.pid, signal.SIGTERM)
        except Exception as error:
            print(error)

        ret_fd.close()

        return flag
