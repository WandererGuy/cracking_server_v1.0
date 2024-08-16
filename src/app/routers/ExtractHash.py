from fastapi import FastAPI, HTTPException, Form, APIRouter
import os 
import uvicorn
import logging
from pydantic import BaseModel
import configparser
import subprocess
from pydantic import BaseModel, validator, ValidationError
from utils.server_utils import *
from fastapi.staticfiles import StaticFiles

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


router = APIRouter()

@router.post ("/ExtractHash") 
async def ExtractHash(    
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
    try:
        check_value_in_list(file_type, support_file_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    extract_hash_result_folder = os.path.join(static_path, "extract_hash_results")
    filename = generate_unique_filename(extract_hash_result_folder)
    extract_hash_result_file = extract_hash_result_folder + '/' + filename

    file_type = data_type_translate(file_type)
    command = gen_extract_command(file_type, clean_path(file_path))
    # command.append('>')
    # command.append(extract_hash_result_file)    
    os.makedirs(os.path.join(static_path,'extract_hash_results'), exist_ok=True)
    try:
        # result = subprocess.run(command, stdout=subprocess.PIPE, text=True)

        result = subprocess.Popen(command, 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Giao tiếp với tiến trình con
        stdout, stderr = result.communicate()

        # In kết quả đầu ra
        # print("Output:", stdout)

        # Kiểm tra và in thông báo lỗi nếu có
        if stderr:
            return {"Errors:": stderr}

        if stdout != None and stdout != "":
            with open (extract_hash_result_file, 'w') as f :
                f.write(stdout)
            path = f"http://{host_ip}:{port_num}/static/extract_hash_results/{filename}"
            return {        
                # "stdout": result.stdout,
                # "stderr": result.stderr,
                "message": "Result saved successfully.",   
                "url":path}
        else:
            return {                
                "message": "Cannot extract file. Something is wrong", 
                "possible error(s)" : "wrong file type\nOR no hash information found in file "
                }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





