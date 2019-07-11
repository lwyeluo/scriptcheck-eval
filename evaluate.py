# coding=utf-8

import argparse

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Evaluate our project")

	parser.add_argument('--run-alexa-top-sites', '-a', action='store_true', help='Run the Alexa top sites')

	parser.add_argument('--run-china-top-sites', '-c', type=int, metavar="MACHINE_INDEX",
						help='Run the China top sites')
	parser.add_argument('--split-china-webpage', '-s', type=int, metavar="NUMBER_OF_MACHINES",
						help='Split the China webpages for multiple machines')

	parser.add_argument('--parse-log', '-p', type=str, choices=['Alexa', 'China'],
						help="Parse the Chrome's logs")
	parser.add_argument('--test-parse-log', '-t', type=str, const="yahoo.com", nargs="?", metavar="DOMAIN",
						help="Test the parser for Chrome's logs.")
	parser.add_argument('--parse-log-with-filename', '-f', type=str, metavar="LOG_FILENAME",
						help="Parse the result for a give log")

	args = parser.parse_args()

	if args.parse_log:

		if args.parse_log == 'Alexa':
			from result_handler import parseAlexaResult

			parseAlexaResult.run()
		elif args.parse_log == 'China':
			from result_handler import parseChinaResult

			parseChinaResult.run()

	elif args.run_alexa_top_sites:
		from run_script import runTopSite

		runTopSite.run()

	elif args.run_china_top_sites != None:
		from run_script import runChinaTopSite

		runChinaTopSite.run(args.run_china_top_sites)

	elif args.split_china_webpage:
		from top_sites_china.split import split

		split(args.split_china_webpage)

	elif args.test_parse_log:
		from result_handler.parseLog import test

		test(args.test_parse_log)
	elif args.parse_log_with_filename:
		from result_handler.parseLog import test_log

		test_log(args.parse_log_with_filename)

	print(args)
