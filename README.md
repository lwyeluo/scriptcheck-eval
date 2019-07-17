## install

```
git pull origin master
# or git clone ...
git submodule update --init --recursive

cd subdomain-tracker
pip3 install -r requirements.txt
cd ../
```

### for sub-domains

```
# get subdomains
python3 evaluate.py -d blog.csdn.net --subdomains
# get the home pages for these subdomains
python3 evaluate.py --parse-homepage -d blog.csdn.net
# crawler urls for these subdomains
...
```

## run

### for China top 500 sites

```
npm install chrome-remote-interface

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
