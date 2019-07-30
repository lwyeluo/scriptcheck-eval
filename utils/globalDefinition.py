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
# for document.domain of Alexa topsites
_target_subdomains_json_file = os.path.join(_topsites_dir, "suspectedSubDomains")

print(">>> _topsites_dir: ", _topsites_dir)
print(">>> _subdomains_dir: ", _subdomains_dir)
print(">>> _target_subdomains_json_file:", _target_subdomains_json_file)