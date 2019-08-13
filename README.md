## some file paths

- Modified Chromium: `~/chromium/tick/src`
- Original Chromium: `~/chromium/init/src`
- Compile the Chromium's source code: `ninja -j4 -C out/Default chrome`

## install

Please use python3.7

```
# in Ubuntu
cd ~/Downloads
sudo apt-get install zlib1g-dev libbz2-dev libssl-dev libncurses5-dev libsqlite3-dev libreadline-dev tk-dev libgdbm-dev libdb-dev libpcap-dev xz-utils libexpat1-dev liblzma-dev libffi-dev libc6-dev
wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz
tar -xzvf Python-3.7.4.tgz
sudo mkdir -p /usr/local/python3.7
cd Python-3.7.4/
./configure --prefix=/usr/local/python3.7 --enable-optimizations
make
sudo make install

sudo update-alternatives --install /usr/bin/python3 python3 /usr/local/python3.7/bin/python3.7 1
sudo update-alternatives --config python3
sudo ln -s /usr/local/python3.7/bin/pip3.7  /usr/bin/pip3
python3 -V
pip3 -V

sudo mv /usr/bin/lsb_release /usr/bin/lsb_release.bak
```

```
git pull origin master
# or git clone ...

cd subdomain-tracker
sudo pip3 install -r requirements.txt
cd ../

cd chromewhip
sudo pip3 install -r requirements.txt
cd ../

sudo pip3 install threadpool publicsuffix numpy

npm install chrome-remote-interface
```

## Visit real world web pages

The commit for Chromium is `0017e185`

Modify Chromium's source code in `base/switcher_impl.h` and `v8/src/runtime/runtime-function.cc`, which adds the logs to record the CPU cycles and time usages

- `base/switcher_impl.h`

```
//#define ENABLE_PERFORMANCE_EVALUATION_FOR_SOP
//#define ENABLE_PERFORMANCE_EVALUATION_FOR_TASK

// whether the chrome logs some metadatas, including frame chain, JS stack...
//   see SWITCHER_RECORD_METADATA in v8/src/runtime/runtime-function.cc
#define SWITCHER_RECORD_METADATA

// whether the switcher should only trust the data from protected memory
//#define SWITCHER_ENABLE_PROTECTION
#define SWITCHER_DISABLE_PROTECTION
```

- `v8/src/runtime/runtime-function.cc`

```
// Added by Luo Wu
//  record the JS function call event
#define SWITCHER_RECORD_METADATA
```

### for sub-domains

```
# get subdomains
python3 evaluate.py --parse-subdomains -d blog.csdn.net
# get the home pages for these subdomains
python3 evaluate.py --parse-homepage -d blog.csdn.net
# crawl urls for these subdomains
python3 evaluate.py --crawl-url -d blog.csdn.net
# run the urls
python3 evaluate.py --run-subdomains -d blog.csdn.net
# parse the logs
python3 evaluate.py --parse-log-for-subdomains -d blog.csdn.net
# or
python3 evaluate.py --parse-log-for-subdomains --all
```

### for Alexa top sites

```
# backup 
rm -rf url_list/topsitesAlexa/results.bak
mv url_list/topsitesAlexa/results url_list/topsitesAlexa/results.bak
# get the home pages
python3 evaluate.py --parse-homepage --Alexa
# crawl urls
python3 evaluate.py --crawl-url --Alexa
# run the urls
python3 evaluate.py --run-alexa-top-sites

# for document.domain
# crawl urls
python3 evaluate.py --crawl-url --Alexa-subdomains
# run the urls
python3 evaluate.py --run-alexa-top-sites --Alexa-subdomains
```

### for benchmark

The commit for Chromium is `0017e185`

#### micro-benchmark

Modify Chromium's source code in `base/switcher_impl.h`, which adds the logs to record the CPU cycles and time usages

```
#define ENABLE_PERFORMANCE_EVALUATION_FOR_SOP
#define ENABLE_PERFORMANCE_EVALUATION_FOR_TASK

// whether the chrome logs some metadatas, including frame chain, JS stack...
//   see SWITCHER_RECORD_METADATA in v8/src/runtime/runtime-function.cc
//#define SWITCHER_RECORD_METADATA

// whether the switcher should only trust the data from protected memory
//#define SWITCHER_ENABLE_PROTECTION
#define SWITCHER_DISABLE_PROTECTION
```

```
python3 evaluate.py --micro-benchmark run
python3 evaluate.py --micro-benchmark parse
```

#### macro-benchmark

Modify Chromium's source code in `base/switcher_impl.h`, which removes the logs for performance test and debugging information, including JS stack, updating frame chain...

```
//#define ENABLE_PERFORMANCE_EVALUATION_FOR_SOP
//#define ENABLE_PERFORMANCE_EVALUATION_FOR_TASK

// whether the chrome logs some metadatas, including frame chain, JS stack...
//   see SWITCHER_RECORD_METADATA in v8/src/runtime/runtime-function.cc
//#define SWITCHER_RECORD_METADATA

// whether the switcher should only trust the data from protected memory
//#define SWITCHER_ENABLE_PROTECTION
#define SWITCHER_DISABLE_PROTECTION
```

- telemetry top_10

    The command to run benchmark is in `benchmark/macro/README.md`

    Parse the log: `python3 evaluate.py --macro-benchmark parse-top10`

- Kraken

    Open the Chromium to visit: `https://krakenbenchmark.mozilla.org/kraken-1.1/driver`

    Parse the log: `python3 evaluate.py --macro-benchmark parse-kraken`

### for China top 500 sites

```
# extract the url list
cd top_sites_china
unrar x result_cn.rar
mv result_cn result
cd ../

# split to 3 machines
python3 evaluate.py -s 3

# run chrome in the machine with ID
python3 evaluate.py -c ID

# parse the log
python3 evaluate.py -p China
```
