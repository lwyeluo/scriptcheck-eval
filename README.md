## some file paths

- Modified Chromium: `~/chromium/tick/src`
- Original Chromium: `~/chromium/init/src`
- Compile the Chromium's source code: `ninja -j4 -C out/Default chrome`

## install

Please use python3.7

```
sudo apt-get install zlib1g-dev libbz2-dev libssl-dev libncurses5-dev libsqlite3-dev libreadline-dev tk-dev libgdbm-dev libdb-dev libpcap-dev xz-utils libexpat1-dev liblzma-dev libffi-dev libc6-dev
sudo apt-get install python3-pip
sudo apt-get install python3-matplotlib
sudo pip3 install threadpool publicsuffix
sudo pip3 install python-whois

# enter tim-evaluate directory and type the command below 
    npm install chrome-remote-interface
```

before running the benchmarks, test it first:

- in terminal 1:

```
cd $CHROME_PATH
# test the chrome binary
out/Default/chrome https://www.baidu.com
# ctrl-c close it
# test nodejs
out/Default/chrome --remote-debugging-port=9222
```

- in terminal 2:

```
# test nodejs
node $tim_evaluate/run_script/run_url_in_Chrome_delay.js https://www.baidu.com 300
```

if the chrome successfully navigate this URL and nodejs finishes by itself, then the test is done!

### for benchmark

The commit for Chromium is `0017e185`

To run the benchmark using our tim_evaluate project:

	Top10(graphic libraries):
	    `python3 evaluate.py --third-benchmark run`
 	Dromaeo:
 	    `python3 evaluate.py --dromaeo-benchmark run`
 	Kraken:
 	    `python3 evaluate.py --kraken-benchmark run`
	DOM-custom:
	    `python3 evaluate.py --dom-benchmark run`
    async-exec:
        `python3 evaluate.py --async-benchmark run`
    sandbox-context:
        `python3 evaluate.py --sandbox-benchmark run`
    telemetry:
        `python3 evaluate.py --telemetry-benchmark run`
    jetstream2:
        `python3 evaluate.py --jetstream2-benchmark run`


To parse the results:
	
	`python3 evaluate.py --third-benchmark parse`
		The data is saved in $tim_evaluate/benchmark/thirdScripts/top10/experiement_data

	`python3 evaluate.py --dromaeo-benchmark parse`
		The data is saved in $tim_evaluate/benchmark/thirdScripts/dromaeo/experiement_data

	`python3 evaluate.py --kraken-benchmark parse`
		The data is in $tim_evaluate/benchmark/macro/kraken/experiement_data

	`python3 evaluate.py --third-benchmark parse`
		The data is saved in $tim_evaluate/benchmark/thirdScripts/top10/experiement_data

	`python3 evaluate.py --dom-benchmark parse`
		The data is saved in $tim_evaluate/benchmark/thirdScripts/dom_yahoo/experiement_data

	`python3 evaluate.py --async-benchmark parse`
		The data is saved in $tim_evaluate/benchmark/thirdScripts/async_exec/experiement_data
		
	`python3 evaluate.py --sandbox-benchmark parse`
		The data is saved in $tim_evaluate/benchmark/thirdScripts/sandbox_context/experiement_data

	`python3 evaluate.py --telemetry-benchmark parse`
		The data is saved in $tim_evaluate/benchmark/macro/top_10/experiement_data

	`python3 evaluate.py --jetstream2-benchmark parse`
		The data is saved in $tim_evaluate/benchmark/thirdScripts/jetstream2/experiement_data

## for Alexa top test

if you need proxy, please configure proxychains4 in your machine, and let `_USE_PROXY_ = True` in `utils/globalDefinition.py`

The domain path is: `url_list/topsitesAlexa/raw_domains`

1. test the homepage whether is reachable

```
python3 evaluate.py --parse-homepage --Alexa
```

2. get more pages for each site

```
python3 evaluate.py --crawl-url --Alexa
```

3. run pages using our chrome

```
python3 evaluate.py --run-alexa-top-sites
```

4. parse logs

```
python3 evaluate.py --parse-log --Alexa
```

## for malicious data set

```
1. run pages using our chrome and baseline

```
python3 evaluate.py --run-malicious-set
```

2. parse logs for our chrome

```
python3 evaluate.py --parse-log --Malicious-set
```

3. parse logs and compare with baseline

```
python3 evaluate.py --parse-log --Malicious-set --compare
```
