# coding=utf-8

import os
import numpy as np

_dir = os.path.dirname(os.path.abspath(__file__))
_fcpfmp_file = os.path.join(_dir, "fcpfmp")
_youtube_file = os.path.join(_dir, "youtube")
_kraken_file = os.path.join(_dir, "kraken")
_sop_file = os.path.join(_dir, "sop")

# colors = ['cornflowerblue','orange','limegreen', 'yellowgreen']

# plot distribution of frame chain
def plotFCPFMP():
	import matplotlib.pyplot as plt
	import matplotlib.ticker as mtick

	# 1. read data
	sites = []
	baseFCPResults, baseFMPResults, timFCPResults, timFMPResults = [], [], [], []
	timFallbackFCPResults, timFallbackFMPResults = [], []
	with open(_fcpfmp_file, "r") as f:
		content = f.readlines()
		# sites
		for t in content[0].strip("\n").split("\t")[1:]:
			sites.append(t.replace(".com", "").replace(".org", "").replace("en.", ""))
		#
		for d in content[1:]:
			data = d.strip("\n").split("\t")
			idx = 0
			if data[idx] == "Baseline-FCP":
				baseFCPResults += [float(x) for x in data[idx+1:]]
			elif data[idx] == "Baseline-FMP":
				baseFMPResults += [float(x) for x in data[idx+1:]]
			elif data[idx] == "TIM-FCP":
				timFCPResults += [float(x) for x in data[idx+1:]]
			elif data[idx] == "TIM-FMP":
				timFMPResults += [float(x) for x in data[idx+1:]]
			elif data[idx] == "TIM-FCP(Fallback)":
				timFallbackFCPResults += [float(x) for x in data[idx+1:]]
			elif data[idx] == "TIM-FMP(Fallback)":
				timFallbackFMPResults += [float(x) for x in data[idx+1:]]
		f.close()

	# plot
	x_label = np.array(sites)
	y1 = np.array(baseFCPResults)
	y2 = np.array(timFallbackFCPResults)
	y3 = np.array(timFCPResults)
	y4 = np.array(baseFMPResults)
	y5 = np.array(timFallbackFMPResults)
	y6 = np.array(timFMPResults)

	x = list(range(len(x_label)))
	total_width, n = 0.8, 6
	width = total_width / n

	hatch = '-'

	plt.figure()
	plt.bar(x, y1, width=width, label="Baseline (FCP)", facecolor='white', edgecolor='black')
	for i in range(0, len(x)):
		x[i] += width
	plt.bar(x, y2, width=width, label="TIM (Fallback) (FCP)", facecolor='#CCCCCC', edgecolor='black')
	for i in range(0, len(x)):
		x[i] += width
	plt.bar(x, y3, width=width, label="TIM (FCP)", facecolor='#666666', edgecolor='black')
	for i in range(0, len(x)):
		x[i] += width
	plt.bar(x, y4, width=width, label="Baseline (FMP)", facecolor='white', hatch=hatch, edgecolor='black')
	for i in range(0, len(x)):
		x[i] += width
	plt.bar(x, y5, width=width, label="TIM (Fallback) (FMP)", facecolor='#CCCCCC', hatch=hatch, edgecolor='black')
	for i in range(0, len(x)):
		x[i] += width
	plt.bar(x, y6, width=width, label="TIM (FMP)", facecolor='#666666', hatch=hatch, edgecolor='black')

	for i in range(len(x)):
		x[i] = x[i] - width * 3
	plt.xticks(x, x_label)

	#plt.ylim(0, 4500)
	plt.tick_params(labelsize=18)
	plt.ylabel('Time usage (ms)', fontproperties='SimHei', fontsize=18)
	plt.grid(axis="y")
	plt.legend(fontsize=15)
	plt.tight_layout()
	plt.show()

def plotYoutube():
	import matplotlib.pyplot as plt
	import matplotlib.ticker as mtick

	# 1. read data
	matrixs, values = [], []
	with open(_youtube_file, "r") as f:
		for d in f.readlines()[1:]:
			data = d.strip("\n").split("\t")
			matrixs.append(data[0])
			values.append(float(data[1]))
		f.close()
	x = np.array(matrixs)
	y = np.array(values)

	plt.figure()
	plt.barh(x, y, edgecolor='white')

	plt.tick_params(labelsize=13)
	plt.xlabel('Time usages (ms)', fontproperties='SimHei', fontsize=18)
	plt.xlim(0, 10000)
	plt.xticks(np.linspace(0, 10000, 6))

	plt.grid(axis='x')
	ax = plt.gca()
	ax.spines['right'].set_color('none')
	ax.spines['top'].set_color('none')
	ax.spines['bottom'].set_color('none')

	plt.tight_layout()
	plt.show()

def plotKraken():
	import matplotlib.pyplot as plt
	import matplotlib.ticker as mtick

	# 1. read data
	types = []
	baseResults, timResults, timFallbackResults = [], [], []
	with open(_kraken_file, "r") as f:
		content = f.readlines()
		for t in content[0].strip("\n").split("\t")[1:]:
			types.append(t.replace(" ", "\n"))
		for d in content[1:]:
			data = d.strip("\n").split("\t")
			if data[0] == "Baseline":
				baseResults += [float(x) for x in data[1:]]
			elif data[0] == "TIM":
				timResults += [float(x) for x in data[1:]]
			elif data[0] == "TIM fallback":
				timFallbackResults += [float(x) for x in data[1:]]
		f.close()
	x_label = np.array(types)
	y1 = np.array(baseResults)
	y2 = np.array(timFallbackResults)
	y3 = np.array(timResults)

	x = list(range(len(x_label)))
	total_width, n = 0.8, 3
	width = total_width / n

	plt.figure()
	plt.bar(x, y1, width=width, label='Baseline', facecolor='white', edgecolor='black')
	for i in range(len(x)):
		x[i] = x[i] + width
	plt.bar(x, y2, width=width, label='Task-based (Fallback)', facecolor='gray', edgecolor='black')
	for i in range(len(x)):
		x[i] = x[i] + width
	plt.bar(x, y3, width=width, label='Task-based', facecolor='black', edgecolor='black')

	for i in range(len(x)):
		x[i] = x[i] - width
	plt.xticks(x, x_label)

	plt.ylim(0, 5500)
	plt.tick_params(labelsize=18)
	plt.ylabel('Time usage (ms)', fontproperties='SimHei', fontsize=18)
	# plt.grid(axis="y")
	plt.legend(fontsize=18)
	plt.tight_layout()
	plt.show()

def plotSOP():
	import matplotlib.pyplot as plt
	import matplotlib.ticker as mtick

	# 1. read data
	types = []
	length, cpus, times = [], [], []
	with open(_sop_file, "r") as f:
		content = f.readlines()
		for t in content[0].strip("\n").split("\t")[1:]:
			types.append(t)
		for d in content[1:]:
			data = d.strip("\n").split("\t")
			length.append(int(data[0]))
			cpus.append(float(data[1]))
			times.append(float(data[2]))
		f.close()
	x = np.array(length)
	y1 = np.array(cpus)
	y2 = np.array(times)

	plt.figure()
	# 定义figure
	fig, ax1 = plt.subplots()
	# 得到ax1的对称轴ax2
	ax2 = ax1.twinx()

	ax1.plot(x, y1, linewidth=2.0, color='gray')
	ax2.plot(x, y2, linewidth=2.0, linestyle='--', color='gray')

	# x轴
	plt.xlim(1, 99)
	plt.xticks(np.linspace(1, 99, 15))
	ax1.tick_params(labelsize=18)
	ax2.tick_params(labelsize=18)

	# y1轴
	ax1.set_ylim(0, 200000)
	# ax1.set_yscale('log')
	# ax1.yaxis.set_major_locator(mtick.LogLocator(base=10.0, numticks=10))

	# y2轴
	ax2.set_ylim(0, 70)

	# 设置label
	ax1.set_xlabel('length of frame chain', fontproperties='SimHei', fontsize=20)
	ax1.set_ylabel(types[0], fontproperties='SimHei', fontsize=20)
	ax2.set_ylabel(types[1], fontproperties='SimHei', fontsize=20)
	ax2.grid(axis="y")

	plt.tight_layout()
	plt.show()


plotFCPFMP()
# plotYoutube()
# plotKraken()
# plotSOP()