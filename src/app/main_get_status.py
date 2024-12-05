from fastapi import FastAPI, HTTPException, Form
# Read the config file
import configparser
import uvicorn
import os 
from routers.model import reply_bad_request, reply_success, reply_server_error
from fastapi.staticfiles import StaticFiles

current_dir = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(current_dir,'static')
hashcat_temp_output = os.path.join(static_path,'hashcat_temp_output.txt')

config = configparser.ConfigParser()
config_path = os.path.join(current_dir, 'config.ini')
config.read(config_path)

host_ip = config['DEFAULT']['host'] 
port_num = config['DEFAULT']['port_status_hash_crack'] 
production = config['DEFAULT']['production']
app = FastAPI()
static_path = os.path.join(current_dir, 'static')
app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/get-hash-crack-status/")
async def get_hash_crack_status():
    # tmp = []
    # with open(hashcat_temp_output, 'r', encoding='utf-8', errors='ignore') as f:
    #     data = f.readlines()
    #     for line in data:
    #         line = line.strip('\n').strip()
    #         tmp.append(line)
    url = f"http://{host_ip}:{port_num}/static/hashcat_temp_output.txt"
    return reply_success(message = "Success retrieve hashcrack status", result = url)

def main():
    print ('INITIALIZING FASTAPI SERVER')
    if not production: uvicorn.run("main:app", host=host_ip, port=int(port_num), reload=True)
    else: uvicorn.run(app, host=host_ip, port=int(port_num), reload=False)

if __name__ == "__main__":
    main()