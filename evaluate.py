# coding=utf-8

import argparse


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Evaluate our project")

	parser.add_argument('--run-top_sites', '-r', action='store_true', help='Run the Alexa top sites')
	parser.add_argument('--run-china-top_sites', '-c', action='store_true', help='Run the China top sites')
	parser.add_argument('--parse-log', '-p', action='store_true', help="Parse the Chrome's logs")

	args = parser.parse_args()

	if args.parse_log:
		from result_handler import parseResult
		parseResult.run()
	elif args.run_top_sites:
		from run_script import runTopSite
		runTopSite.run()
	elif args.run_china_top_sites:
		from run_script import runChinaTopSite
		runChinaTopSite.run()
