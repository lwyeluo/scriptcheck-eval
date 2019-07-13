```
npm install chrome-remote-interface

cd top_sites_china
unrar x result_cn.rar
mv result_cn result

# split to 3 machines
cd ../
python3 evaluate.py -s 3

# run chrome in the machine with ID
python3 evaluate.py -c ID

# parse the log
python3 evaluate.py -p China
```
