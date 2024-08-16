from fastapi import FastAPI, HTTPException, Form
import os 
import uvicorn
import logging
from pydantic import BaseModel
import configparser
import subprocess
from pydantic import BaseModel, validator, ValidationError
from utils.server_utils import *
from fastapi.staticfiles import StaticFiles
from routers.HashCrack import router as HashCrack_router
from routers.ExtractHash import router as ExtractHash_router 
from routers.prince import router as prince_router 

from starlette.responses import RedirectResponse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='fastapi.log', filemode='w')
logger = logging.getLogger(__name__)

# Get the directory where the current script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to config.ini
config_path = os.path.join(script_dir, 'config.ini')

# Read the config file
config = configparser.ConfigParser()
config.read(config_path)

host_ip = config['DEFAULT']['host'] 
port_num = config['DEFAULT']['port'] 

app = FastAPI()
app.include_router(HashCrack_router)
app.include_router(ExtractHash_router)
app.include_router(prince_router)


static_path = os.path.join(script_dir, 'static')
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def root():
    """
    # Redirect
    to documentation (`/docs/`).
    """
    return RedirectResponse(url="/docs/")


def main():
    print ('INITIALIZING FASTAPI SERVER')
    uvicorn.run("main:app", host=host_ip, port=int(port_num), reload=True)



if __name__ == "__main__":
    main()
