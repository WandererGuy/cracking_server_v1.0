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
from utils.prince_hashcat import *
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(detail)s', filename='fastapi.log', filemode='w')
logger = logging.getLogger(__name__)

# Get the directory where the current script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to config.ini
config_path = os.path.join(script_dir, '..', 'config.ini')

# Construct the path to config.ini
static_path = os.path.join(script_dir, '..','static')

prince_run_file = os.path.join(script_dir, '..','..','prince','pp64.bin')

crack_collection = os.path.join(static_path, 'cracked_hashes.txt')
cracked_hash_result_folder = os.path.join(static_path,'cracked_hash')
prince_wordlist_folder = os.path.join(static_path,'prince_wordlist_output')

# Read the config file
config = configparser.ConfigParser()
config.read(config_path)
host_ip = config['DEFAULT']['host'] 
port_num = config['DEFAULT']['port'] 
pot_file = config['DEFAULT']['pot_file'] 

router = APIRouter()

@router.post("/prince-generate/")
async def prince_generate(    
    prince_wordlist: str = Form(...),   # prince wordlist
    keyspace: bool = Form(False),         # Calculate number of combinations
    pw_min: int = Form(None),           # Print candidate if length is greater than NUM
    pw_max: int = Form(None),           # Print candidate if length is smaller than NUM
    elem_cnt_min: int = Form(None),     # Minimum number of elements per chain
    elem_cnt_max: int = Form(None),     # Maximum number of elements per chain
    wl_dist_len: bool = Form(False),  # Calculate output length distribution from wordlist
    wl_max: int = Form(None),           # Load only NUM words from input wordlist or use 0 to disable
    dupe_check_disable: bool = Form(False), # Disable dupes check for faster initial load
    save_pos_disable: bool = Form(False),   # Save the position for later resume with -s
    skip: int = Form(None),             # Skip NUM passwords from start (for distributed)
    limit: int = Form(None),            # Limit output to NUM passwords (for distributed)
    # output_file: str = Form(None),    # Output-file
    case_permute: bool = Form(False),    # For each word in the wordlist that begins with a letter
                                        # generate a word with the opposite case of the first letter
):
    try:
        prince_command = genPrinceCommandNormal(
                        prince_run_file=prince_run_file,
                        prince_wordlist=prince_wordlist,
                        keyspace=keyspace,
                        pw_min=pw_min,
                        pw_max=pw_max,
                        elem_cnt_min=elem_cnt_min,
                        elem_cnt_max=elem_cnt_max,
                        wl_dist_len=wl_dist_len,
                        wl_max=wl_max,
                        dupe_check_disable=dupe_check_disable,
                        save_pos_disable=save_pos_disable,
                        skip=skip,
                        limit=limit,
                        # output_file=output_file,
                        case_permute=case_permute
                        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e), data={"url": None})
    try:
        filename = generate_unique_filename(prince_wordlist_folder)
        prince_wordlist_file = os.path.join(prince_wordlist_folder,filename)
        prince_command.append('>')
        prince_command.append(prince_wordlist_file)
        process = subprocess.Popen(' '.join(prince_command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)

        _, stderr = process.communicate()
        if stderr:
            raise HTTPException(status_code=400, detail=stderr, data={"url": None})

        path = f"http://{host_ip}:{port_num}/static/prince_wordlist_output/{filename}"
        data={"detail":"Result saved successfully." ,"data":{"url":path}}

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail = {"message":str(e), "data": {"url":None}})

                            



@router.post("/prince-hashcat/")
async def prince_hashcat(    
    prince_wordlist: str = Form(...),   # prince wordlist
    # keyspace: bool = Form(False),         # Calculate number of combinations
    pw_min: int = Form(None),           # Print candidate if length is greater than NUM
    pw_max: int = Form(None),           # Print candidate if length is smaller than NUM
    elem_cnt_min: int = Form(None),     # Minimum number of elements per chain
    elem_cnt_max: int = Form(None),     # Maximum number of elements per chain
    # wl_dist_len: bool = Form(False),  # Calculate output length distribution from wordlist
    wl_max: int = Form(None),           # Load only NUM words from input wordlist or use 0 to disable
    dupe_check_disable: bool = Form(False), # Disable dupes check for faster initial load
    save_pos_disable: bool = Form(False),   # Save the position for later resume with -s
    skip: int = Form(None),             # Skip NUM passwords from start (for distributed)
    limit: int = Form(...),            # Limit output to NUM passwords (for distributed)
    # output_file: str = Form(None),    # Output-file
    case_permute: bool = Form(False),    # For each word in the wordlist that begins with a letter
                                        # generate a word with the opposite case of the first letter
    hash_type: str = Form(...),
    hash_file: str = Form(...), 
    # wordlist: str = Form(...), 
    attack_mode: str = Form(...),
    rule_path: str = Form(None)
):
    try:
        prince_command = genPrinceCommandHashcat(
                        prince_run_file=prince_run_file,
                        prince_wordlist=prince_wordlist,
                        # keyspace=keyspace,
                        pw_min=pw_min,
                        pw_max=pw_max,
                        elem_cnt_min=elem_cnt_min,
                        elem_cnt_max=elem_cnt_max,
                        # wl_dist_len=wl_dist_len,
                        wl_max=wl_max,
                        dupe_check_disable=dupe_check_disable,
                        save_pos_disable=save_pos_disable,
                        skip=skip,
                        limit=limit,
                        case_permute=case_permute
                        )
    except Exception as e:
        raise HTTPException(status_code=500, detail = {"message":str(e), "data": {"url":None}})


    try:
        filename = generate_unique_filename(cracked_hash_result_folder)
        cracked_hash_result_file = os.path.join(cracked_hash_result_folder,filename)
        hashcat_command = gen_hashcat_command(
                        hash_type, 
                        hash_file , 
                        # wordlist , 
                        attack_mode,
                        rule_path 
                        )
        prince_command.append('|')
        full_command = prince_command
        for i in hashcat_command:
            full_command.append(i)

        # piping '|'require shell feature so shell = True 
        process = subprocess.Popen(' '.join(full_command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)


        _, stderr = process.communicate()


        if stderr:
            raise HTTPException(status_code=400, detail = {"message":stderr, "data": {"url":None}})



        # Giao tiếp với tiến trình con
        full_command.append('--show')
        process = subprocess.Popen(' '.join(full_command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)

        stdout, stderr = process.communicate()
    
        if stderr:
            raise HTTPException(status_code=400, detail = {"message":stderr, "data": {"url":None}})


        if stdout == '' or stdout == None:
            return {        
            "detail": "Wordlist Exhausted. Cannot crack hash",
            "data":
            {
            "url": None
            }   
            }
        with open(cracked_hash_result_file, 'w') as f:
            f.write(stdout)

        with open(crack_collection, 'a') as f:
            f.writelines(stdout)
        crack_collection_url = crack_collection.split("/static",1)[1]
        crack_collection_url = '/static' + crack_collection_url
        path = f"http://{host_ip}:{port_num}/static/cracked_hash/{filename}"
        bonus_path = f"http://{host_ip}:{port_num}{crack_collection_url}"
        data={"detail":"Result saved successfully." ,
                "data": 
                {
                "url":path, 
                "bonus_detail": "Already cracked hash before will be stored in.",   
                "bonus_url":bonus_path
                }
        }
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail= {"message":str(e), "data": {"url":None}})


