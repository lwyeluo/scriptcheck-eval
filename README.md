## for China top 500 sites

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

## for sub-domains

```
domain=chinacloudsites.cn

# get the subdomains
cd subdomain-tracker
pip install -r requirements.txt
python sublist3r.py -b -t 16 -d $domain -o url_list/subdomains/$domain -v
```
