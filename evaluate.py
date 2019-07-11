# coding=utf-8

import argparse

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Evaluate our project")

	parser.add_argument('--run-alexa-top-sites', '-a', action='store_true', help='Run the Alexa top sites')
	parser.add_argument('--run-china-top-sites', '-c', action='store_true', help='Run the China top sites')
	parser.add_argument('--parse-log', '-p', action='store_true', help="Parse the Chrome's logs")
	parser.add_argument('--test-parse-log', '-t', type=str, const="yahoo.com", nargs="?",
						help="Test the parser for Chrome's logs. The domain is [TEST_PARSE_LOG]")

	args = parser.parse_args()

	if args.parse_log:
		from result_handler import parseResult

		parseResult.run()
	elif args.run_alexa_top_sites:
		from run_script import runTopSite

		runTopSite.run()
	elif args.run_china_top_sites:
		from run_script import runChinaTopSite

		runChinaTopSite.run()
	elif args.test_parse_log:
		from result_handler.parseLog import test

		test(args.test_parse_log)