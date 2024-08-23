from fastapi import FastAPI, HTTPException, Form, APIRouter
import os 
import uvicorn
import logging
from pydantic import BaseModel
import configparser
import subprocess
from pydantic import BaseModel, validator, ValidationError
from utils.extract_hash import *
from fastapi.staticfiles import StaticFiles
from utils.common import *


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='fastapi.log', filemode='w')
logger = logging.getLogger(__name__)

# Get the directory where the current script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to config.ini
config_path = os.path.join(script_dir, '..', 'config.ini')

# Read the config file
config = configparser.ConfigParser()
config.read(config_path)
host_ip = config['DEFAULT']['host'] 
port_num = config['DEFAULT']['port'] 
pot_file = config['DEFAULT']['pot_file'] 

script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to config.ini
static_path = os.path.join(script_dir, '..','static')

extract_hash_result_folder = os.path.join(static_path, "extract_hash_results")
os.makedirs((extract_hash_result_folder), exist_ok=True)

router = APIRouter()

@router.post ("/extract-hash") 
async def extract_hash(    
    file_type: str = Form(...),
    file_path: str = Form(...)
    ):
    # print support file type
    # available_keys = list_value_in_dict(support_file_type)

    """
    Description:<br>
    this endpoint used to extract hash(es) from locked/encrypted file with password<br>
    <br>
    Input: <br>
    file_type : type of file be extracted<br>
    supported file type : MD5, BitLocker, 7-Zip, WinZip, RAR<br> 
    file_path : path to file to be extracted<br>
    Expected response :<br>
    url to file txt with hash extracted 
    """
    detail = check_value_in_list(file_type, support_file_type)
    if detail is not True:
        raise HTTPException(status_code=400,detail = {"message":detail, "data": {"url":None}})

        
    filename = generate_unique_filename(extract_hash_result_folder)
    extract_hash_result_file = extract_hash_result_folder + '/' + filename

    file_type = data_type_translate(file_type)
    command = gen_extract_command(file_type, clean_path(file_path))
    try:
        stdout, stderr = execute_command(command)
        # Kiểm tra và in thông báo lỗi nếu có
        path = f"http://{host_ip}:{port_num}/static/extract_hash_results/{filename}"

        if stdout == None or stdout == "":
            detail = "Cannot extract file.\nPossibilities: wrong file type\nOR no hash information found in file"
            raise HTTPException(status_code=400,detail = {"message":detail, "data": {"url":None}})

        if stderr:
            detail = handle_stderr(stderr)
            raise HTTPException(status_code=400,detail = {"message":detail, "data": {"url":None}})

        return handle_stdout(stdout, path, extract_hash_result_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail= {"message":str(e), "data": {"url":None}})





