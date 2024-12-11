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

from contextlib import asynccontextmanager
from routers.extract_hash import find_hashcat_hash_code


app = FastAPI()
app.mount("/static", StaticFiles(directory=static_path), name="static")
app.add_exception_handler(MyHTTPException, my_exception_handler)




@app.get("/get-hash-crack-status/")
async def get_hash_crack_status():
    url = f"http://{host_ip}:{port_num}/static/hashcat_temp_output.txt"
    return reply_success(message = "Success retrieve hashcrack status", result = url)


@app.get("/get-backend-status/")
async def get_backend_status():
    url = f"http://{host_ip}:{port_num}/static/backend_temp_output.txt"
    return reply_success(message = "Success retrieve backend status", result = url)

@app.post("/find-code/")
async def find_code(
    hash_file: str = Form(...),
):
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
    with open (path, 'w') as f:
        for key, value in collect_res.items():
            f.write(f'Hash: {key}\n')
            f.write(f'Hashcat Hash Code: {value}\n\n\n')
    
    return reply_success(message = "Success", result = {"url":url, "path":fix_path(path)})

def main():
    print ('INITIALIZING FASTAPI SERVER')
    if empty_to_false(production) == False: 
        uvicorn.run("main_status:app", host=host_ip, port=int(port_num), reload=True)
    else: uvicorn.run(app, host=host_ip, port=int(port_num), reload=False)

if __name__ == "__main__":
    main()