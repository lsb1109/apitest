from multiprocessing import *

q = Queue()
p = Process(target=sub_process_code, args=(q, ))
p.start()
selected_data = q.get()

contents_name = selected_data[1][selected_data[2]]

if selected_data[0] == 0:
    second_code = extract_code(main_link + str(contents_name) + py_code_file)
    exec(second_code)

elif selected_data[0] == 1:
    excel = win32.Dispatch("Excel.Application")
    excel.Visible = True
    workbook = excel.Workbooks.Open(local_xl_path + contents_name)

else:
    pass