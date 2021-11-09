# coding=utf-8

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Evaluate our project")

    '''
		Helper
	'''
    parser.add_argument('--domain', '-d', type=str, metavar="DOMAIN", help="The domain.")
    parser.add_argument('--all', action='store_true', help="All possible targets.")
    parser.add_argument('--Alexa', action='store_true', help="For Alexa top sites.")
    parser.add_argument('--test', action='store_true', help="For the test.")
    parser.add_argument('--Alexa-subdomains', action='store_true', help="For subdomains of Alexa top sites.")
    parser.add_argument('--reverse', action='store_true', help="Reversely run sites.")
    parser.add_argument('--machine-id', type=int, metavar="MACHINE_INDEX",
                        help='Run the top sites in machine MACHINE_INDEX')
    parser.add_argument('--save', action='store_true', help="Save the temporary objects.")
    parser.add_argument('--load', action='store_true', help="Load the temporary objects.")
    parser.add_argument('--script', type=str, metavar="SCRIPT", help="The name of 3rd script.")

    '''
		Handle URL List
	'''
    # --parse-subdomains -d DOMAIN
    parser.add_argument('--parse-subdomains', action='store_true',
                        help='Parse the sub-domains for a given domain. Use it with -d')
    # --parse-homepage -d DOMAIN | --parse-homepage -f LIST_FILE | --parse-homepage --Alexa
    parser.add_argument('--parse-homepage', action='store_true',
                        help='For subdomains, parse the homepage-list for a DOMAIN (with -d) or site-list (with -f).'
                             'For top sites, use with --Alexa')
    # -s NUMBER_OF_MACHINE
    parser.add_argument('--split', '-s', type=int, metavar="NUMBER_OF_MACHINES",
                        help='Split the webpages for multiple machines')
    # --crawl-url -d DOMAIN | --crawl-url --Alexa
    parser.add_argument('--crawl-url', action='store_true',
                        help='For subdomains, crawl urls for a DOMAIN (with -d).'
                             'For top sites, use with --Alexa. '
                             'For document.domain of top sites. use with --Alexa-subdomains')

    '''
		Parse Log
	'''
    # --parse-log China|Alexa
    parser.add_argument('--parse-log', action='store_true',
                        help="Parse the Chrome's logs for Alexa|China top sites")
    # -f LOG_FILE -d DOMAIN
    parser.add_argument('--parse-log-with-filename', '-f', type=str, metavar="LOG_FILENAME",
                        help="Parse the result for a give log. Use it with -d.")
    # --parse-log-for-subdomains -d DOMAIN
    parser.add_argument('--parse-log-for-subdomains', action='store_true',
                        help="Parse the subdomains' logs for a give DOMAIN (with -d)")

    '''
		Run Script
	'''
    # --run-alexa-top-sites
    parser.add_argument('--run-alexa-top-sites', action='store_true',
                        help='Run the Alexa top sites. '
                        'For document.domain of top sites. use with --Alexa-subdomains. '
                        'For reversely running top site, use with --reverse. '
                        'For running top site in multiple machines, use with --machine-id MACHINE_ID. ')
    # --run-subdomains -d DOMAIN
    parser.add_argument('--run-subdomains', action='store_true',
                        help="Run the subdomain's url-list for a DOMAIN (with -d)")


    '''
        Benchmark
    '''
    parser.add_argument('--micro-benchmark', type=str, choices=['run', 'parse'],
                        help="Run | Parse the micro-benchmark to record the CPU cycles")
    parser.add_argument('--third-benchmark', type=str, choices=['run', 'parse'],
                        help="Run | Parse the third-benchmark to test the performance")
    parser.add_argument('--async-benchmark', type=str, choices=['run', 'parse'],
                        help="Run | Parse the async-benchmark to test the performance")
    parser.add_argument('--security-monitor-benchmark', type=str, choices=['run', 'parse'],
                        help="Run | Parse the security-monitor-benchmark to test the performance")
    parser.add_argument('--kraken-benchmark', type=str, choices=['run', 'parse'],
                        help="Run | Parse the kraken-benchmark to test the performance")
    parser.add_argument('--dromaeo-benchmark', type=str, choices=['run', 'parse'],
                        help="Run | Parse the dromaeo-benchmark to test the performance")
    parser.add_argument('--sandbox-benchmark', type=str, choices=['run', 'parse', 'run_cross', 'run_except_cross'],
                        help="Run | Parse the sandbox-benchmark to test the performance")
    parser.add_argument('--telemetry-benchmark', type=str, choices=['run', 'parse'],
                        help="Run | Parse the telemetry-benchmark to test the performance")
    parser.add_argument('--jetstream2-benchmark', type=str, choices=['run', 'parse'],
                        help="Run | Parse the jetstream2-benchmark to test the performance")
    parser.add_argument('--speedometer-benchmark', type=str, choices=['run', 'parse'],
                        help="Run | Parse the speedometer-benchmark to test the performance")


    args = parser.parse_args()

    ####################################################
    #	Handle URL List
    ####################################################
    if args.parse_homepage:
        # --parse-homepage -d DOMAIN | --parse-homepage --Alexa
        if args.domain:
            from url_crawler.subdomains import run

            run(args.domain)
        elif args.Alexa:
            from top_sites.homePageForTopsitesAlexa import run

            run()
        else:
            raise Exception("Please use '--parse-homepage -d DOMAIN' or '--parse-homepage --Alexa' ")

    elif args.crawl_url:
        # --crawl-url -d DOMAIN | --crawl-url --Alexa
        if args.domain:
            from url_crawler.crawler import run

            run(args.domain, type="SubDomain")
        elif args.Alexa:
            from url_crawler.crawler import run

            run(None, type='Alexa')
        elif args.Alexa_subdomains:
            from document_domain.crawlSubDomainURL import run

            run()
        else:
            raise Exception("Please use '--parse-url -d DOMAIN' or '--parse-url -f LIST_FILE' ")

    elif args.parse_subdomains:
        # --parse-subdomains -d DOMAIN
        if not args.domain:
            raise Exception("Please use --parse-subdomains -d DOMAIN")

        from url_list.findSubDomains import run

        run(args.domain)

    elif args.split:
        # -s NUMBER_OF_MACHINE --Alexa
        if args.Alexa:
            from url_list.split import split

            split(args.split)
        else:
            raise Exception("Please use --split NUMBER_OF_MACHINE --Alexa")

    ####################################################
    #	Parse Log
    ####################################################

    elif args.parse_log:
        # --parse-log --Alexa
        if args.Alexa:
            from result_handler.third_js import parseResult

            if args.test:
                parseResult.test()
            else:
                parseResult.run()
        else:
            raise Exception("Use --parse-log China|Alexa")

    elif args.parse_log_with_filename and args.domain:
        # -f LOG_FILE -d DOMAIN
        from result_handler.parseLog import test_log

        test_log(args.parse_log_with_filename, args.domain)

    elif args.parse_log_for_subdomains:
        from result_handler.parseSubdomainsResult import run

        if args.domain:
            # --parse-log-for-subdomains -d DOMAIN
            run(args.domain)
        else:
            raise Exception("Please use '--parse-log-for-subdomains -d DOMAIN'")

    ####################################################
    #	Run Script
    ####################################################
    elif args.run_subdomains:
        # --run-subdomains -d DOMAIN
        if not args.domain:
            raise Exception("Please use --run-subdomains -d DOMAIN")

        from run_script.runSubDomains import run

        run(args.domain)

    elif args.run_alexa_top_sites:
        # --run-alexa-top-sites --Alexa-subdomains
        if args.Alexa_subdomains:
            from document_domain.runSubDomains import run

            run()
        elif args.reverse:
            from top_sites import runTopSiteReverse

            runTopSiteReverse.run()
        elif args.machine_id is not None:
            from top_sites import runTopSiteWithMultiMachines

            runTopSiteWithMultiMachines.run(args.machine_id)
        else:
            # --run-alexa-top-sites
            from top_sites import runTopSite

            runTopSite.run()

    ####################################################
    #	Test
    ####################################################

    elif args.test_parse_log:
        # -t DOMAIN
        from result_handler.parseLog import test

        test(args.test_parse_log)

    ####################################################
    #	Benchmark
    ####################################################

    elif args.micro_benchmark:
        if args.micro_benchmark == "run":
            # --micro-benchmark run
            from benchmark.micro.run import run

            run()
        elif args.micro_benchmark == "parse":
            # --micro-benchmark parse
            from benchmark.micro.parseResult import run

            run()

    elif args.telemetry_benchmark:
        if args.telemetry_benchmark == "run":
            # --telemetry-benchmark run
            from benchmark.macro.top10.runTelemetry import run

            run()
        elif args.telemetry_benchmark == "parse":
            # --telemetry-benchmark parse
            from benchmark.macro.top10.parseResult import run

            run()

    elif args.third_benchmark:
        if args.third_benchmark == "run":
            # --third-benchmark run
            from benchmark.thirdScripts.library.run import run

            run(args.script)
        elif args.third_benchmark == "parse":
            # --third-benchmark parse
            from benchmark.thirdScripts.library.parseResult import run

            run()
    elif args.async_benchmark:
        if args.async_benchmark == "run":
            # --async-benchmark run
            from benchmark.thirdScripts.async_exec.run import run

            run()
        elif args.async_benchmark == "parse":
            # --async-benchmark parse
            from benchmark.thirdScripts.async_exec.parse import run

            run()

    elif args.security_monitor_benchmark:
        if args.security_monitor_benchmark == "run":
            # --security-monitor-benchmark run
            from benchmark.thirdScripts.security_monitor.run import run

            run()
        elif args.security_monitor_benchmark == "parse":
            # --security-monitor-benchmark run
            from benchmark.thirdScripts.security_monitor.parseResult import run

            run()

    elif args.kraken_benchmark:
        if args.kraken_benchmark == "run":
            # --kraken-benchmark run
            from benchmark.thirdScripts.kraken.run import run

            run()
        elif args.kraken_benchmark == "parse":
            # --kraken-benchmark parse
            from benchmark.thirdScripts.kraken.parseResult import run

            run()

    elif args.dromaeo_benchmark:
        if args.dromaeo_benchmark == "run":
            # --dromaeo_benchmark run
            from benchmark.thirdScripts.dromaeo.run import run

            run()
        elif args.dromaeo_benchmark == "parse":
            # --dromaeo_benchmark parse
            from benchmark.thirdScripts.dromaeo.parseResult import run

            run()

    elif args.sandbox_benchmark:
        if args.sandbox_benchmark == "run":
            # --sandbox_benchmark run
            from benchmark.thirdScripts.sandbox_context.run import run

            run()
        if args.sandbox_benchmark == "run_cross":
            # --sandbox_benchmark run_cross
            from benchmark.thirdScripts.sandbox_context.run import run_cross

            run_cross()
        if args.sandbox_benchmark == "run_except_cross":
            # --sandbox_benchmark run_except_cross
            from benchmark.thirdScripts.sandbox_context.run import run_except_cross

            run_except_cross()
        elif args.sandbox_benchmark == "parse":
            # --sandbox_benchmark parse
            from benchmark.thirdScripts.sandbox_context.parse import run

            run()
    elif args.jetstream2_benchmark:
        if args.jetstream2_benchmark == "run":
            # --jetstream2_benchmark run
            from benchmark.thirdScripts.jetStream2.run import run

            run()
        elif args.jetstream2_benchmark == "parse":
            # --jetstream2_benchmark parse
            from benchmark.thirdScripts.jetStream2.parse import run

            run()

    elif args.speedometer_benchmark:
        if args.speedometer_benchmark == "run":
            # --speedometer_benchmark run
            from benchmark.thirdScripts.speedometer.run import run

            run()
        elif args.speedometer_benchmark == "parse":
            # --speedometer_benchmark parse
            from benchmark.thirdScripts.speedometer.parseResult import run

            run()

    print("\n")
    print(args)
