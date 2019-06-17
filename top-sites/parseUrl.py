import os
_top_site_dir = os.path.dirname(__file__)
_raw_url_filename = os.path.join(_top_site_dir, "raw_url")
_final_url_filename = os.path.join(_top_site_dir, "final_url")
print(_raw_url_filename, _final_url_filename)

_raw_fd, _final_fd = open(_raw_url_filename, "r"), open(_final_url_filename, 'w')

for line in _raw_fd.readlines():
    arr = line.strip("\n").split("\t")
    if arr == ['']:
        continue

    final_url = ""

    if arr[3] in ['ok', '403']:
        arr[1] = "https://" + arr[1]
    elif arr[3] in ['', 'y'] and arr[2] == '':
        arr[1] = "https://" + arr[1]
    elif arr[2] == 'x':
        final_url += "#"
    elif arr[2] == 'www':
        arr[1] = "https://www." + arr[1]
    elif arr[2] == 'http':
        arr[1] = "http://" + arr[1]
    elif arr[2] == 'httpwww':
        arr[1] = "http://www." + arr[1]
    else:
        raise Exception("you have not handled: " + " ".join(arr))
    
    print(final_url + "\t".join(arr))
    _final_fd.write(final_url + "\t".join(arr) + "\n")

_raw_fd.close()
_final_fd.close()