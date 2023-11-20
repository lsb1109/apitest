import requests
import winreg

import ast

import streamlit as st
import pandas as pd

import time

# fmt: off

converter_path = "https://raw.githubusercontent.com/lsb1109/apitest/main/api_id_convert.json"
converter_get = requests.get(converter_path)
converter = ast.literal_eval(converter_get.content.decode("utf8"))

host_uri = "https://api-beta.midasit.com/cim"
converter_keys = list(converter.keys())
method_list = ["get", "post", "patch", "put", "delete"]
req_fun_list = [requests.get, requests.post, requests.patch, requests.put, requests.delete]
ui_lock_opt = 0

global_css = """
  <style>
    .st-emotion-cache-16txtl3 {
        margin-top: -70px;
    }
    .st-emotion-cache-z5fcl4 {
        margin-top: -70px;
    }
    .st-emotion-cache-64tehz {
        gap: 16px;
    }
    hr {
        margin: 0px auto;
    }
  </style>
"""

# 최초 페이지 세팅
st.set_page_config(layout="wide")
st.title("User Custom csv Runner")

class DataConverter:
    def data_type_convert(data, type):
        function_name = "convert_" + type.replace(" ", "_")
        new_data = getattr(DataConverter, function_name)(data)
        return new_data

    def convert_scalar(data):
        temp_data = float(data)
        return temp_data

    def convert_option(data):
        temp_data = int(data)
        return temp_data

    def convert_integer(data):
        temp_data = int(data)
        return temp_data

    def convert_string(data):
        temp_data = data
        return temp_data

    def convert_point(data):
        temp_data = data
        return temp_data

    def convert_scalar_array(data):
        data = data.replace(" ", "")
        temp_data = [float(i) for i in data.split(",")]
        return temp_data

    def convert_select(data):
        data = data.replace(" ", "")
        temp_list = data.split(",")
        temp_data = ",".join(temp_list)
        return temp_data

    def convert_boolean(data):
        if data.lower() == "true" or data == "1":
            temp_data = True
        elif data.lower() == "false" or data == "0":
            temp_data = False
        return temp_data

class TextFormatRunner:
    def reg2apikey():
        key = winreg.HKEY_CURRENT_USER
        key_value = "SOFTWARE\MIDAS\midas CIM\APISetting"
        api_connect_reg = winreg.OpenKey(key, key_value, 0, winreg.KEY_ALL_ACCESS)
        api_key_value, api_key_type = winreg.QueryValueEx(api_connect_reg, "APIKey")
        header = {"MAPI-Key": api_key_value}
        return header

    def request_function(input_method, uri, body):
        method_index = method_list.index(input_method)
        header = getattr(TextFormatRunner, "reg2apikey")()
        temp_request = req_fun_list[method_index](uri, headers=header, json=body)
        return temp_request

    def json_decomposition(json):
        temp_keys = list(json.keys())
        temp_index = 0
        temp_json = json[temp_keys[temp_index]]
        tester = temp_json[0]
        types = []
        jsons = []
        if type(tester[list(tester.keys())[0]]) != list:
            types.append("")
            jsons.append(temp_json)
        else:
            for i in temp_json:
                types.append("_" + list(i.keys())[0])
                jsons.append(list(i.values())[0])
        return types, jsons

    def valid_dict_convert(valid_dict, convert_opt):
        old_id = [i["old_id"] for i in valid_dict]
        new_id = [i["new_id"] for i in valid_dict]
        if convert_opt == 0:
            used_dict = dict(zip(old_id, new_id))
        else:
            used_dict = dict(zip(new_id, old_id))
        return used_dict

    def json_convert(function_json, org_json, convert_opt):
        global error_code
        corvert_info_json = function_json["convert_info"]
        
        used_dict = getattr(TextFormatRunner, "valid_dict_convert")(corvert_info_json, convert_opt)
        valid_ids = list(used_dict.keys())
        data_type = [i["type"] for i in corvert_info_json]
        new_json = []
        for i in org_json:
            if i["id"] in valid_ids:
                try:
                    i["value"] = DataConverter.data_type_convert(
                        i["value"], data_type[valid_ids.index(i["id"])]
                    )
                    i["id"] = used_dict[i["id"]]
                    new_json.append(i)
                except:
                    error_code = 3
                    return False
            else:
                error_code = 2
                return False
        # /file의 경우 array type이 아닌 object type
        if function_json["path"] == "/file":
            new_json = new_json[0]
        return new_json

    def csv_save(df):
        df.to_csv(".csv")

    def req_df_separate(df):
        used_df = df
        separator_list = used_df[0].values
        temp_list = []
        for i in range(len(separator_list)):
            if "*" in separator_list[i]:
                temp_list.append(i)
        temp_list.append(used_df.shape[0])
        temp_dfs = []

        for i in range(len(temp_list) - 1):
            temp_dfs.append(used_df.iloc[temp_list[i] : temp_list[i + 1], :])        
        return temp_dfs

    def api_run(df):
        global error_code, response
        error_code = None
        try:
            dfs = getattr(TextFormatRunner, "req_df_separate")(df)
        except:
            error_code = 6
            getattr(TextFormatRunner, "message_call")("s")
            return
        break_loc = None
        for i in dfs:
            break_test = True
            now_index = i.iloc[0].name + 1
            i = i.reset_index(drop=True)
            fuction_name = i.iloc[0, 0][1:].lower()
            api_method = i.iloc[0, 1].lower()
            if fuction_name not in converter_keys or api_method not in method_list:
                break_loc = now_index
                error_code = 1
                break_test = False
                break
            i.drop([0], axis=0, inplace=True)

            now_index = now_index + 1
            target_function = converter[fuction_name]
            uri_path = target_function["path"]
            result_uri = host_uri + uri_path + "?apply=true"
            
            # empty Check (Body가 [], {}인 경우 즉시 Request)
            if i.empty:
                response = getattr(TextFormatRunner, "request_function")(api_method, result_uri, [])
                pass
            else:
                dict_keys = i.iloc[[0]].values[0]
                nan_column_loc = []
                key_column_loc = []
                ignore_column_loc = []
                for j in range(len(dict_keys)):
                    if type(dict_keys[j]) != str:
                        nan_column_loc.append(j)
                    else:
                        if dict_keys[j][0] == ";":
                            key_column_loc.append(j)
                        elif dict_keys[j][0] == "_":
                            ignore_column_loc.append(j)

                if len(key_column_loc) == 1:
                    entity_key_list = i.iloc[:, key_column_loc[0]].values.tolist()[1:]

                elif len(key_column_loc) > 1:
                    break_loc = now_index
                    error_code = 2
                    break_test = False
                    break

                i.drop(nan_column_loc + key_column_loc + ignore_column_loc, axis=1, inplace=True)
                dict_keys = [j.lower() for j in i.iloc[[0]].values[0]]
                i.drop([1], axis=0, inplace=True)

                now_index = now_index + 1
            for j in range(i.shape[0]):
                if len(key_column_loc) == 1:
                    result_uri = host_uri + uri_path + str(entity_key_list[j]) + "&apply=true"
                if api_method == "get":
                    try:
                        if len(dict_keys) == 1 and dict_keys[0] == "file name":
                            response = getattr(TextFormatRunner, "request_function")(api_method, result_uri, [])
                            res_json = response.json()
                            types, jsons = getattr(TextFormatRunner, "json_decomposition")(res_json)
                            for k in range(len(types)):
                                res_df = pd.DataFrame(jsons[k])
                                getattr(TextFormatRunner, "csv_save")(res_df, i.iloc[j].to_list()[0] + types[k])
                        else:
                            break_loc = now_index
                            error_code = 2
                            break_test = False
                            break
                    except:
                        break_loc = now_index
                        error_code = 5
                        break_test = False
                        break
                        
                else:
                    dict_values = i.iloc[j].to_list()
                    request_json = []
                    for k in range(len(dict_keys)):
                        data_set = {}
                        data_set["id"] = dict_keys[k]
                        data_set["value"] = dict_values[k]
                        request_json.append(data_set)
                    new_json = getattr(TextFormatRunner, "json_convert")(target_function, request_json, 1)
                    if new_json != False:
                        response = getattr(TextFormatRunner, "request_function")(api_method, result_uri, new_json)
                        if response.status_code > 300:
                            break_loc = now_index + j
                            break_test = False
                            error_code = 4
                            break
                    else:
                        break_loc = now_index + j
                        break_test = False
                        break
            
            if break_test == False:
                break
        
        getattr(TextFormatRunner, "message_call")(break_loc)

    def message_call(row):
        if row == None:
            status = ("[" + time.strftime("%X") + "] " + "Done")
        else:
            error_message = getattr(TextFormatRunner, "error_response")()
            status = "[" + time.strftime("%X") + "] " + "Check your csv <Row:" + str(row) + "> \n" + error_message

    def error_response():
        if error_code == 1:
            message = "<Error:" + str(error_code) + " | Function Name Error>"
        elif error_code == 2:
            message = "<Error:" + str(error_code) + " | Field Name Error>"
        elif error_code == 3:
            message = "<Error:" + str(error_code) + " | Data Error>"
        elif error_code == 4:
            message = "<Error:" + str(error_code) + " | API Response NG>\nResponse = " + response.text
        elif error_code == 5:
            message = "<Error:" + str(error_code) + " | File Create Error>"
        elif error_code == 6:
            message = "<Error:" + str(error_code) + " | CSV Format Error>"
        return message

empty_page = st.empty()

def csv2df():
    temp_csv = pd.read_csv(uploaded_file, header=None)
    temp_df = temp_csv.dropna(how="all")
    return temp_df

def test(df):
    keys = df.index.to_list()
    separator_list = used_df[0].values
    temp_list = []
    for i in range(len(separator_list)):
        if "*" in separator_list[i]:
            temp_list.append(keys[i])
    return temp_list

def df_preview(df, num):
    empty_page.subheader("csv Preview")
    st.dataframe(df.style.applymap(lambda _: "background-color: CornflowerBlue;", subset=(num, slice(None))), width= 3000, height= 900)
    st.sidebar.markdown("----", unsafe_allow_html=True)
    st.sidebar.success("CSV Read Success" + " [" + time.strftime("%X") + "]")

st.markdown(global_css, unsafe_allow_html=True)
st.sidebar.title("Input")
st.sidebar.markdown("----", unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("*.csv 파일을 업로드하세요.", type="csv")

st.sidebar.markdown("----", unsafe_allow_html=True)
test_btn = st.sidebar.button("Run test")

if uploaded_file is not None:
    used_df = csv2df()
    num = test(used_df)
    df_preview(used_df, num)
    
if test_btn:
    TextFormatRunner.api_run(used_df)
