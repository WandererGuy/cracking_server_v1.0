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
current_dir = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(current_dir,'static')
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

async def periodic_request():
    while True:
        try:
            with open(backend_temp_step, 'r') as f:
                content = f.read()
            write_backend_status(content)
            print('update backend status')
        except Exception as e:
            print(f"An error occurred: {e}")
        await asyncio.sleep(5)  # Wait for 5 seconds before the next request

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(periodic_request()) # start up action 
    print("Started periodic HTTP requests every 5 seconds.")
    yield
    pass # shutdown action 
app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=static_path), name="static")
app.add_exception_handler(MyHTTPException, my_exception_handler)

def write_backend_status(content):
    with open(backend_temp_output, 'w', encoding='utf-8') as f:
        if 'generating' in content.lower() or 'validating' in content.lower():
            f.write(content)
        else: 
            f.write(content)
            f.write('\n\n')
            with open(hashcat_temp_output, 'r', encoding='utf-8') as f_hc:
                progress = f_hc.read() 
            f.write(progress)

@app.get("/get-hash-crack-status/")
async def get_hash_crack_status():
    url = f"http://{host_ip}:{port_num}/static/hashcat_temp_output.txt"
    return reply_success(message = "Success retrieve hashcrack status", result = url)


@app.get("/get-backend-status/")
async def get_backend_status():
    url = f"http://{host_ip}:{port_num}/static/backend_temp_output.txt"
    return reply_success(message = "Success retrieve backend status", result = url)

@app.post("/find_code/")
async def find_code(
    hash_file: str = Form(...),
):
    collect_res = {}
    with open(hash_file, 'r') as f:
        hashes = f.readlines()
        hashes = list(set(hashes))
        for index, hash in enumerate(hashes):
            hash = hash.strip('\n').strip()
            real_hash = hash
            hashcat_hash_code = find_hashcat_hash_code(hash_file, real_hash)

            if hashcat_hash_code == None:
                message = f'Cannot find hashcat hash_code for remaining hashes. \
                    Maybe hash extracted wrong or not hash not supported by system'
                return reply_bad_request(message)
            else:
                collect_res[real_hash] = hashcat_hash_code
    with open ()


def main():
    print ('INITIALIZING FASTAPI SERVER')
    if empty_to_false(production) == False: 
        uvicorn.run("main_status:app", host=host_ip, port=int(port_num), reload=True)
    else: uvicorn.run(app, host=host_ip, port=int(port_num), reload=False)

if __name__ == "__main__":
    main()