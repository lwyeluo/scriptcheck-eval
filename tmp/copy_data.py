# coding-=utf-8

import os
from utils.executor import execute

'''
	@root_dir: referring to the corresponding tim-evaluate
'''
def calcResultsPath(root_dir):
	_topsite_dir = os.path.join(os.path.join(root_dir, "url_list"), "topsitesAlexa")
	return os.path.join(_topsite_dir, "results")

def copy_data(reverse_dir, smu_dir):
	for dir in os.listdir(reverse_dir):
		if os.path.exists(os.path.join(smu_dir, dir)):
			continue
		s_dir = os.path.join(reverse_dir, dir)
		d_dir = os.path.join(smu_dir, dir)
		cmd = "mv %s %s" % (s_dir, d_dir)
		print(cmd)
		execute(cmd)

def show_state(smu_dir):
	sites_num = execute("ls %s/results | wc -l" % os.path.dirname(smu_dir))
	pages_num = execute("find %s/results -type f | wc -l" % os.path.dirname(smu_dir))
	print(">>> sites_num = %s, pages_num = %s" % (sites_num, pages_num))

if __name__ == '__main__':
	_dir = os.path.abspath(os.path.dirname(__file__))
	_project_dir = os.path.dirname(_dir)
	_bak_dir = os.path.join(os.path.dirname(_project_dir), "bak")
	_bak_project_dir = os.path.join(_bak_dir, "tim-evaluate")

	_reverse_results_dir = calcResultsPath(_bak_project_dir)
	_smu_results_dir = calcResultsPath(_project_dir)

	print(_reverse_results_dir, _smu_results_dir)

	# copy_data
	copy_data(_reverse_results_dir, _smu_results_dir)
	show_state(_smu_results_dir)




