import os
import json
from pip._internal import main

import requests
from bs4 import BeautifulSoup

version_key_type = ["tool_ver", "py_app_ver", "xl_app_ver", "js_app_ver"]
selector_list = ["base/", "python_app/", "excel_app/", "javascript_app/"]

git_raw_link = "https://raw.githubusercontent.com/lsb1109/apitest/main/"

local_contents_path = r"C:\Temp\CIM_API_APP\\"

version_json = "app_version.json"
package_txt = "requirements.txt"

def extract_soup( link):
    req = requests.get(link)
    req.encoding = None
    html = req.content
    soup = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
    return soup

def version_compare(target_type, content_name):
    temp_json_path = local_contents_path + version_json
    selector = selector_list[version_key_type.index(target_type)]
    if not os.path.isfile(temp_json_path):
        if not os.path.exists(local_contents_path):
            os.makedirs(local_contents_path)
        default_dic = {version_key_type[0]: {}, version_key_type[1]: {},
                        version_key_type[2]: {}, version_key_type[3]: {}}
        with open(temp_json_path, "w") as f:
            json.dump(default_dic, f)

    json_soup = extract_soup(git_raw_link + selector +  content_name + "/" + version_json)
    app_ver_dict = json.loads(str(json_soup))        
    current_app_key = list(app_ver_dict.keys())[0]
    current_app_ver = list(app_ver_dict.values())[0]

    with open(temp_json_path, "r") as f:
        all_dict = json.load(f)
    target_old_dict = all_dict[target_type]
    last_app_ver = target_old_dict.get(current_app_key)

    if last_app_ver and last_app_ver == current_app_ver:
        pass
    else:
        print("import 관련 함수 실행 코드 추가")
        txt_soup = extract_soup(git_raw_link + selector +  content_name + "/" + package_txt)            
        lines = str(txt_soup).splitlines()
        for temp_pkg in lines:
            main(["install", temp_pkg])
        target_old_dict.update({current_app_key: current_app_ver})
        all_dict.update({target_type: target_old_dict})
        with open(temp_json_path, "w") as f:
            json.dump(all_dict, f)

version_compare("tool_ver", "01_app_selection")