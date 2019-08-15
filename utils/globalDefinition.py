import string
import os
from utils.executor import execute

# for randomize the file name
_random_sample = string.ascii_letters + string.digits

_dir = os.path.abspath(os.path.dirname(__file__))
_log_filename = os.path.join(os.path.dirname(_dir), "result-run-script.log")

_tmp_dir = os.path.join(os.path.dirname(_dir), "tmp")

_run_script_dir = os.path.join(os.path.dirname(_dir), "run_script")

_url_list_dir = os.path.join(os.path.dirname(_dir), 'url_list')
# for subdomains
_subdomains_dir = os.path.join(_url_list_dir, "subdomains")
# for Alexa topsites
_topsites_dir = os.path.join(_url_list_dir, "topsitesAlexa")
_topsites_split_dir = os.path.join(_topsites_dir, "site-split")
_topsites_reachable_file = os.path.join(_topsites_dir, "reachable_domains")
_topsites_urls_dir = os.path.join(_topsites_dir, "urls")
# for document.domain of Alexa topsites
_target_subdomains_json_file = os.path.join(_topsites_dir, "suspectedSubDomains")

print(">>> _topsites_dir: ", _topsites_dir)
print(">>> _subdomains_dir: ", _subdomains_dir)
print(">>> _target_subdomains_json_file:", _target_subdomains_json_file)


_http_headers = {
    'pragma': "no-cache",
    'accept-encoding': "gzip, deflate, br",
    'accept-language': "zh-CN,zh;q=0.8",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'cache-control': "no-cache",
    'connection': "keep-alive",
}


# for performance

# get the home directory
_home_dir = execute("echo $HOME")
# get the chrome binary
_chrome_binary = _home_dir + "/chromium/tick/src/out/Default/chrome"
print("Chrome binary is ", _chrome_binary)
# get the node binary
_node_binary = "node"
# get the nodejs script, which checks the loading status and gets domains for all same-origin frames
_node_filename = os.path.join(_run_script_dir, "find_recursive_subframes.js")
# nodejs to run a given url in Chrome
_node_run_url_filename = os.path.join(_run_script_dir, "run_url_in_Chrome.js")
# timeout for each webpage
_timeout = 300
_timeout_for_node = 30
_timeout_benchmark = 300
_timeout_for_node_benchmark = 300
# the caches for Chrome
_cache_for_Chrome_filepath = _home_dir + "/.config/chromium/Default"
