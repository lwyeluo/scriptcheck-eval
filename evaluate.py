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
    parser.add_argument('--Alexa-subdomains', action='store_true', help="For subdomains of Alexa top sites.")
    parser.add_argument('--reverse', action='store_true', help="Reversely run sites.")
    parser.add_argument('--machine-id', type=int, metavar="MACHINE_INDEX",
                        help='Run the top sites in machine MACHINE_INDEX')

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
    parser.add_argument('--parse-log', type=str, choices=['Alexa', 'China'],
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
		Test
	'''
    # -t DOMAIN
    parser.add_argument('--test-parse-log', '-t', type=str, const="yahoo.com", nargs="?", metavar="DOMAIN",
                        help="Test the parser for Chrome's logs.")

    args = parser.parse_args()

    ####################################################
    #	Handle URL List
    ####################################################
    if args.parse_homepage:
        # --parse-homepage -d DOMAIN | --parse-homepage -f LIST_FILE | --parse-homepage --Alexa
        if args.domain:
            from url_crawler.subdomains import run

            run(args.domain)
        elif args.parse_log_with_filename:
            # TODO
            pass
        elif args.Alexa:
            from top_sites.homePageForTopsitesAlexa import run

            run()
        else:
            raise Exception("Please use '--parse-url -d DOMAIN' or '--parse-url -f LIST_FILE' ")

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
        # --parse-log  China|Alexa

        if args.parse_log in ['Alexa', 'China']:
            from result_handler import parseResult

            parseResult.run(args.parse_log)
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
        elif args.machine_id:
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

    print("\n")
    print(args)
