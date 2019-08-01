import string
import os

# for randomize the file name
_random_sample = string.ascii_letters + string.digits

_dir = os.path.abspath(os.path.dirname(__file__))
_log_filename = os.path.join(os.path.dirname(_dir), "result-run-script.log")

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