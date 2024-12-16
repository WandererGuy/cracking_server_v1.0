from fastapi import FastAPI, HTTPException, Form
# Read the config file
import configparser
import uvicorn
import os 
from routers.model import reply_bad_request, reply_success, reply_server_error
from fastapi.staticfiles import StaticFiles
from utils.common import empty_to_false
from routers.model import MyHTTPException, my_exception_handler
import requests 
import asyncio
import uuid 
from utils.common import fix_path
current_dir = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(current_dir,'static')
hashcat_hash_code_folder = os.path.join(static_path,'backend','hashcat_hash_code')
hash_dump_folder = os.path.join(static_path,'backend','hash_dump')

hashcat_temp_output = os.path.join(static_path,'hashcat_temp_output.txt')
backend_temp_output = os.path.join(static_path,'backend_temp_output.txt')
backend_temp_step = os.path.join(static_path,'backend_temp_step.txt')

config = configparser.ConfigParser()
config_path = os.path.join(current_dir, 'config.ini')
config.read(config_path)

host_ip = config['DEFAULT']['host'] 
port_num = config['DEFAULT']['port_status_hash_crack'] 
production = config['DEFAULT']['production']
num_workers = int(config['DEFAULT']['num_workers'])
from contextlib import asynccontextmanager
from routers.extract_hash import find_hashcat_hash_code
import pandas as pd 
from utils.session_handle import main as create_a_session
app = FastAPI()
app.mount("/static", StaticFiles(directory=static_path), name="static")
app.add_exception_handler(MyHTTPException, my_exception_handler)

def session_save(session_folder_path, hash_file, res):
    excel_path = os.path.join(session_folder_path, 'session.xlsx')
    df = pd.read_excel(excel_path)
    os.makedirs(session_folder_path, exist_ok=True)
    for hash, hashcat_hash_code in res.items():
        name_single_hash_file = str(uuid.uuid4()) + '.txt'
        folder_1 = os.path.join(session_folder_path, hashcat_hash_code)
        file_1 = os.path.join(folder_1, name_single_hash_file)
        all_same_hashcat_hash_code_file = os.path.join(folder_1, 'all.txt')
        os.makedirs(file_1, exist_ok=True)
        with open(file_1, 'w') as f:
            f.write(hash)
        with open(all_same_hashcat_hash_code_file, 'a') as f:
            f.write(hash)
            f.write('\n')
        new_row = {
                'hash value in file': file_1, 
                'original extracted file path': "", 
                'original hash file path': hash_file, 
                'hashcat hash code': hashcat_hash_code, 
                'hashes same hashcat hash code in file': all_same_hashcat_hash_code_file, 
                'plaintext password': ""
                }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(excel_path, index=False)

@app.get("/get-hash-crack-status/")
async def get_hash_crack_status():
    url = f"http://{host_ip}:{port_num}/static/hashcat_temp_output.txt"
    return reply_success(message = "Success retrieve hashcrack status", result = url)


@app.get("/get-backend-status/")
async def get_backend_status():
    url = f"http://{host_ip}:{port_num}/static/backend_temp_output.txt"
    return reply_success(message = "Success retrieve backend status", result = {"url":url})

@app.post("/find-code/")
async def find_code(
    session_name : str = Form(...),
    hash_file: str = Form(...)
    
):
    session_folder_path = os.path.join(static_path, 'session', session_name)
    if os.path.exists(hash_file) == False:
        message = f"file_path {fix_path(hash_file)} does not exist"
        return reply_bad_request(message = message)
    if os.path.exists(session_folder_path) == False:
        message = f"session_folder_path {fix_path(session_folder_path)} does not exist"
        return reply_bad_request(message = message)
    fail_message = f'Cannot find hashcat hash_code. Maybe hash is wrong OR not supported by system'
    filename_0 = str(uuid.uuid4()) + '.txt'
    path_0 = os.path.join(hash_dump_folder, filename_0)

    collect_res = {}
    with open(hash_file, 'r') as f:
        hashes = f.readlines()
        hashes = list(set(hashes))
        for real_hash in hashes:
            real_hash = real_hash.strip('\n').strip()
            if real_hash == "":
                continue 
            with open(path_0, 'w') as f_0:
                f_0.write(real_hash)
            hashcat_hash_code = find_hashcat_hash_code(path_0, real_hash)
            if hashcat_hash_code == None:
                collect_res[real_hash] = fail_message
            else:
                collect_res[real_hash] = hashcat_hash_code
    filename = str(uuid.uuid4()) + '.txt'
    path = os.path.join(hashcat_hash_code_folder, filename)
    url = f"http://{host_ip}:{port_num}/static/backend/hashcat_hash_code/{filename}"
    # with open (path, 'w') as f:
    #     for key, value in collect_res.items():
    #         f.write(f'Hash: {key}\n')
    #         f.write(f'Hashcat Hash Code: {value}\n\n\n')
    session_save(session_folder_path, 
                              hash_file, 
                              collect_res)
    # result = {"path":path, "url":url}
    result = None
    return reply_success(message = "Success", result = result)

@app.get("/create-session/")
async def create_session(
):
    session_name = create_a_session()
    return reply_success(message = "Success", result = {"session_name":session_name})

@app.post("/get-status-session/")
async def get_status_session(
    session_name : str = Form(...)

):
    session_path = os.path.join(static_path, 'session', session_name)
    if os.path.exists(session_path) == False:
        message = f"session_folder_path {session_name} does not exist"
        return reply_bad_request(message = message)

    session_excel_path = fix_path(os.path.join(session_path, 'session.xlsx'))
    return reply_success(message = "Success", result = {"session_excel_path":session_excel_path})

def main():
    print ('INITIALIZING FASTAPI SERVER')
    if empty_to_false(production) == False: 
        uvicorn.run("main_status:app", host=host_ip, port=int(port_num), reload=True, workers = num_workers)
    else: uvicorn.run("main_status:app", host=host_ip, port=int(port_num), reload=False, workers = num_workers)

if __name__ == "__main__":
    main()