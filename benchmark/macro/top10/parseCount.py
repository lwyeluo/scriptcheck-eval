# coding=utf-8

import os

absolutePath = os.path.abspath(__file__)
countFile = os.path.dirname(absolutePath) + "/../result/telemetry/tmp-1"

_features_cnt_switch_task = ">>> [COUNT] enter Switcher::doSwitch"
_features_cnt_update_frame_chain = ">>> [COUNT] enter SWITCHER_TASK_HELPER::doPrincipalSwitchImplUpdateFrameChain"
_features_run_webpage = "[ RUN      ]"
_features_stop_webpage = "[       OK ]"

_key_switch_task = "switchTask"
_key_update_frame_chain = "updateFrameChain"

def run():
	cur_webpage = ""
	results = {}
	with open(countFile, "r", encoding="ISO-8859-1") as f:
		while True:
			line = f.readline()
			if not line:
				break

			if _features_run_webpage in line:
				_, _, webpage = line.strip("\n").partition(_features_run_webpage)
				print(webpage)
				cur_webpage = webpage
				if cur_webpage not in results.keys():
					results[cur_webpage] = [{_key_switch_task: 0, _key_update_frame_chain: 0}]
				else:
					results[cur_webpage].append({_key_switch_task: 0, _key_update_frame_chain: 0})
			elif _features_cnt_switch_task in line:
				results[cur_webpage][-1][_key_switch_task] += 1
			elif _features_cnt_update_frame_chain in line:
				results[cur_webpage][-1][_key_update_frame_chain] += 1

		f.close()

	print(results)


if __name__ == '__main__':
	run()