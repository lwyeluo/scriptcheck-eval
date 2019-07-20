# coding=utf-8

import argparse

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Evaluate our project")

	'''
		Helper
	'''
	parser.add_argument('--domain', '-d', type=str, metavar="DOMAIN", help="The domain.")

	'''
		Handle URL List
	'''
	# --parse-subdomains -d DOMAIN
	parser.add_argument('--parse-subdomains', action='store_true',
						help='Parse the sub-domains for a given domain. Use it with -d')
	# --parse-homepage -d DOMAIN | --parse-homepage -f LIST_FILE
	parser.add_argument('--parse-homepage', action='store_true',
						help='Parse the homepage-list for a DOMAIN (with -d) or site-list (with -f)')
	# -s NUMBER_OF_MACHINE
	parser.add_argument('--split-china-webpage', '-s', type=int, metavar="NUMBER_OF_MACHINES",
						help='Split the China webpages for multiple machines')

	'''
		Parse Log
	'''
	# -p China|Alexa
	parser.add_argument('--parse-log', '-p', type=str, choices=['Alexa', 'China'],
						help="Parse the Chrome's logs")
	# -f LOG_FILE -d DOMAIN
	parser.add_argument('--parse-log-with-filename', '-f', type=str, metavar="LOG_FILENAME",
						help="Parse the result for a give log. Use it with -d.")

	'''
		Run Script
	'''
	# -a
	parser.add_argument('--run-alexa-top-sites', '-a', action='store_true', help='Run the Alexa top sites')
	# -c MACHINE_ID
	parser.add_argument('--run-china-top-sites', '-c', type=int, metavar="MACHINE_INDEX",
						help='Run the China top sites')
	# --run-subdomains -d DOMAIN
	parser.add_argument('--run-subdomains', action='store_true',
						help="Run the subdomain's url-list for a DOMAIN (with -d)")

	'''
		Test
	'''
	# -t DOMAIN
	parser.add_argument('--test-parse-log', '-t', type=str, const="yahoo.com", nargs="?", metavar="DOMAIN",
						help="Test the parser for Chrome's logs.")

	args = parser.parse_args()

	if args.parse_homepage:
		# --parse-homepage -d DOMAIN | --parse-homepage -f LIST_FILE
		if args.domain:
			from url_crawler.subdomains import run

			run(args.domain)
		elif args.parse_log_with_filename:
			# TODO
			pass
		else:
			raise Exception("Please use '--parse-url -d DOMAIN' or '--parse-url -f LIST_FILE' ")

	elif args.parse_subdomains:
		# --parse-subdomains -d DOMAIN
		if not args.domain:
			raise Exception("Please use --parse-subdomains -d DOMAIN")

		from url_list.findSubDomains import run

		run(args.domain)

	elif args.run_subdomains:
		# --run-subdomains -d DOMAIN
		if not args.domain:
			raise Exception("Please use --run-subdomains -d DOMAIN")

		from run_script.runSubDomains import run

		run(args.domain)

	elif args.parse_log:
		# -p China|Alexa

		if args.parse_log == 'Alexa':
			from result_handler import parseAlexaResult

			parseAlexaResult.run()
		elif args.parse_log == 'China':
			from result_handler import parseChinaResult

			parseChinaResult.run()

	elif args.run_alexa_top_sites:
		# -a
		from run_script import runTopSite

		runTopSite.run()

	elif args.run_china_top_sites != None:
		# -c MACHINE_ID
		from run_script import runChinaTopSite

		runChinaTopSite.run(args.run_china_top_sites)

	elif args.split_china_webpage:
		# -s NUMBER_OF_MACHINE
		from top_sites_china.split import split

		split(args.split_china_webpage)

	elif args.test_parse_log:
		# -t DOMAIN
		from result_handler.parseLog import test

		test(args.test_parse_log)
	elif args.parse_log_with_filename and args.domain:
		# -f LOG_FILE -d DOMAIN
		from result_handler.parseLog import test_log

		test_log(args.parse_log_with_filename, args.domain)

	print("\n")
	print(args)
