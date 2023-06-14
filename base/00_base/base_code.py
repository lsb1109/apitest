local_xl_path = r"C:\Temp\CIM_API_APP\\"
py_link_root = "https://raw.githubusercontent.com/lsb1109/apitest/main/python_app/"
main_code_name = "/main_code.py"

q = Queue()
p = Process(target=sub_process_code, args=(q, ))
p.start()
selected_data = q.get()

contents_name = selected_data[1]
print(contents_name)

if selected_data[0] == 0:
    second_code = extract_code(py_link_root + str(contents_name) + main_code_name)
    exec(second_code)

elif selected_data[0] == 1:
    excel = win32.Dispatch("Excel.Application")
    excel.Visible = True
    workbook = excel.Workbooks.Open(local_xl_path + contents_name + "/" + contents_name + ".xlsm")

else:
    pass