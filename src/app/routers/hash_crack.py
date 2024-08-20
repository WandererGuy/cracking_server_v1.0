from fastapi import FastAPI, HTTPException, Form, APIRouter
import os 
import uvicorn
import logging
from pydantic import BaseModel
import configparser
import subprocess
from pydantic import BaseModel, validator, ValidationError
from utils.common import *
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

# Construct the path to config.ini
static_path = os.path.join(script_dir, '..','static')

crack_collection = os.path.join(static_path, 'cracked_hashes.txt')


router = APIRouter()
@router.post("/hash-crack/")
async def hash_crack(    
    hash_type: str = Form(...),
    hash_file: str = Form(...), 
    wordlist: str = Form(...), 
    attack_mode: str = Form(...),
    rule_path: str = Form(None)
    ):
    """
    Hashcat crack given hash using wordlist/masklist. <br>
    Input:<br>
        hash_type : type of the hash<br>
        wordlist : wordlist path / masklist path<br>
        attack_mode : attacking mode <br>

    Note:<br>
        supported hash type: MD5, BitLocker, 7-Zip, WinZip, RAR5<br>
        supported attack type: Straight, Combination, Brute-force, Hybrid Wordlist + Mask, Hybrid Mask + Wordlist, Association<br>
    Expected response :<br>
        urrl to file with plaintext of given hash if cracked 
    """
    try:
        # Check if the value exists in the dictionary keys
        check_value_in_dict(attack_mode, attack_mode_dict)
        check_value_in_dict(hash_type, hash_type_dict)     

        hash_type = str(data_type_translate(hash_type))
        hash_file = clean_path(hash_file)
        wordlist = clean_path(wordlist)
        rule_path = clean_path(rule_path)

        attack_mode = str(attack_mode_translate(attack_mode))

        
        cracked_hash_result_folder = os.path.join(static_path, 'cracked_hash')
        filename = generate_unique_filename(cracked_hash_result_folder)
        cracked_hash_result_file = os.path.join(cracked_hash_result_folder,filename)
        # Build the Hashcat command
        command = [
            'hashcat',
            '-m', hash_type,       # Hash type
            '-a', attack_mode,             # Attack mode
            hash_file,            # Hash
            wordlist,               # Wordlist
        ]
        if rule_path != None and rule_path != '':
            command.append('-r')
            command.append(rule_path)
        # Run the command

        process = subprocess.Popen(command, 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        _, stderr = process.communicate()
        if stderr:
            raise HTTPException(status_code=400, detail=f"Errors: {stderr}")


        # Giao tiếp với tiến trình con
        command = [
            'hashcat',
            '-m', hash_type,       # Hash type
            '-a', attack_mode,             # Attack mode
            hash_file,            # Hash
            wordlist,               # Wordlist
            '--show'
        ]
        process = subprocess.Popen(command, 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        if stderr:
            raise HTTPException(status_code=400, detail=f"Errors: {stderr}")


        if stdout == '' or stdout == None:
            return {        
            "message": "Wordlist Exhausted. Cannot crack hash"
            }   
        with open(cracked_hash_result_file, 'w') as f:
            f.write(stdout)

        with open(crack_collection, 'a') as f:
            f.writelines(stdout)

        path = f"http://{host_ip}:{port_num}/static/cracked_hash/{filename}"
        crack_collection_url = crack_collection.split("/static",1)[1]
        crack_collection_url = '/static' + crack_collection_url
        bonus_path = f"http://{host_ip}:{port_num}{crack_collection_url}"

        return {        
            "message": "Result saved successfully.",   
            "url":path,
            "bonus_message": "Already cracked hash before will be stored in.",   
            "bonus_url":bonus_path
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
