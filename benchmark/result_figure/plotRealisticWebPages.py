# coding=utf-8

import os
import numpy as np

_dir = os.path.dirname(os.path.abspath(__file__))
_frame_chain_file = os.path.join(_dir, "framechain")
_main_frame_file = os.path.join(_dir, "mainframe")
_embed_frame_file = os.path.join(_dir, "embedframe")

# plot distribution of frame chain
def plotFrameChain():
	import matplotlib.pyplot as plt
	import matplotlib.ticker as mtick

	# 1. read data
	length, webpages, percentage = [], [], []
	with open(_frame_chain_file, "r") as f:
		for d in f.readlines()[1:]:
			data = d.strip("\n").split("\t")
			length.append(int(data[0]))
			webpages.append(int(data[1]))
			percentage.append(float(data[3])*100)
		f.close()
	x = np.array(length)
	y = np.array(webpages)
	y2 = np.array(percentage)

	plt.figure()
	# 定义figure
	fig, ax1 = plt.subplots()
	# 得到ax1的对称轴ax2
	# ax2 = ax1.twinx()

	ax1.bar(x, y, facecolor="gray", edgecolor="white")
	# ax2.plot(x, y2, color='red', linewidth=2.0, linestyle='--')

	# x轴
	plt.xlim(1, 99)
	plt.xticks(np.linspace(1, 99, 15))
	ax1.tick_params(labelsize=20)
	# ax2.tick_params(labelsize=13)

	# y1轴
	ax1.set_ylim(10 ** 0, 10 ** 5)
	ax1.set_yscale('log')
	ax1.yaxis.set_major_locator(mtick.LogLocator(base=10.0, numticks=10))

	# y2轴
	# ax2.set_ylim(0, 100)
	# ax2.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0f%%'))

	# 设置label
	ax1.set_xlabel('Length of longest frame chain', fontproperties='SimHei',fontsize=22)
	ax1.set_ylabel('Number of web pages', fontproperties='SimHei',fontsize=22)
	# ax2.set_ylabel('probability accumulation', fontproperties='SimHei',fontsize=15)

	plt.tight_layout()
	plt.show()

def plotMainFrame():
	import matplotlib.pyplot as plt
	import matplotlib.ticker as mtick

	# 1. read data
	sites, numberOfEmbeddedSites = [], []
	with open(_main_frame_file, "r") as f:
		for d in f.readlines()[1:]:
			data = d.strip("\n").split("\t")
			sites = [data[0]] + sites
			numberOfEmbeddedSites = [int(data[2])] + numberOfEmbeddedSites
		f.close()
	x = np.array(sites)
	y = np.array(numberOfEmbeddedSites)

	plt.figure()
	plt.barh(x, y, facecolor="gray", edgecolor="black")

	plt.tick_params(labelsize=18)
	plt.xlabel('Number of embedded sites', fontproperties='SimHei', fontsize=18)
	plt.xlim(17, 21)
	ax = plt.gca()
	ax.xaxis.set_ticks_position('top')
	ax.xaxis.set_label_position('top')

	plt.grid(axis='x')
	ax = plt.gca()
	ax.spines['right'].set_color('none')
	# ax.spines['top'].set_color('none')
	ax.spines['bottom'].set_color('none')

	plt.tight_layout()
	plt.show()

def plotEmbeddedFrame():
	import matplotlib.pyplot as plt
	import matplotlib.ticker as mtick

	# 1. read data
	sites, numberOfMainSites = [], []
	with open(_embed_frame_file, "r") as f:
		for d in f.readlines()[2:]:
			data = d.strip("\n").split("\t")
			sites = [data[2]] + sites
			numberOfMainSites = [int(data[0])] + numberOfMainSites
		f.close()
	x = np.array(sites)
	y = np.array(numberOfMainSites)

	plt.figure()
	plt.barh(x, y, facecolor="gray", edgecolor="black")

	plt.tick_params(labelsize=18)
	plt.xlabel('Number of host sites', fontproperties='SimHei', fontsize=18)
	plt.xlim(0, 1800)
	plt.xticks(np.linspace(0, 1800, 4))
	ax = plt.gca()
	ax.xaxis.set_ticks_position('top')
	ax.xaxis.set_label_position('top')

	plt.grid(axis='x')
	ax = plt.gca()
	ax.spines['right'].set_color('none')
	#ax.spines['top'].set_color('none')
	ax.spines['bottom'].set_color('none')

	plt.tight_layout()
	plt.show()


plotFrameChain()
plotMainFrame()
plotEmbeddedFrame()