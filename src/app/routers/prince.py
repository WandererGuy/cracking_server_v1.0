from fastapi import Form, APIRouter
import os 
import logging
import configparser
import subprocess
from utils.common import *
from utils.prince_hashcat import *
from routers.model import reply_bad_request, reply_success, reply_server_error

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(detail)s', filename='fastapi.log', filemode='w')
logger = logging.getLogger(__name__)
# Get the directory where the current script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to config.ini
parent_dir = os.path.dirname(script_dir)    
config_path = os.path.join(parent_dir, 'config.ini')

# Construct the path to config.ini
static_path = os.path.join(parent_dir,'static')
prince_run_file = os.path.join(os.path.dirname(parent_dir),'prince','pp64.bin')
crack_collection = os.path.join(static_path, "potfiles", "potfile.txt")
cracked_hash_result_folder = os.path.join(static_path,'cracked_hash')
prince_wordlist_folder = os.path.join(static_path,'prince_wordlist_output')

# Read the config file
config = configparser.ConfigParser()
config.read(config_path)
host_ip = config['DEFAULT']['host'] 
port_num = config['DEFAULT']['port'] 

router = APIRouter()

@router.post("/prince-generate/")
async def prince_generate(    
    prince_wordlist: str = Form(...),   # prince wordlist
    keyspace: bool = Form(False),         # Calculate number of combinations
    pw_min: str = Form(None),           # Prstr candidate if length is greater than NUM
    pw_max: str = Form(None),           # Prstr candidate if length is smaller than NUM
    elem_cnt_min: str = Form(None),     # Minimum number of elements per chain
    elem_cnt_max: str = Form(None),     # Maximum number of elements per chain
    wl_dist_len: bool = Form(False),  # Calculate output length distribution from wordlist
    wl_max: str = Form(None),           # Load only NUM words from input wordlist or use 0 to disable
    dupe_check_disable: bool = Form(False), # Disable dupes check for faster initial load
    save_pos_disable: bool = Form(False),   # Save the position for later resume with -s
    skip: str = Form(None),             # Skip NUM passwords from start (for distributed)
    limit: str = Form(None),            # Limit output to NUM passwords (for distributed)
    # output_file: str = Form(None),    # Output-file
    case_permute: bool = Form(False),    # For each word in the wordlist that begins with a letter
                                        # generate a word with the opposite case of the first letter
):
    if not os.path.exists(prince_wordlist):
        message = f"file_path {prince_wordlist} does not exist"
        return reply_bad_request(message = message)

        # Convert empty strings to None for optional parameters
    pw_min = empty_to_none(pw_min)
    pw_max = empty_to_none(pw_max)
    elem_cnt_min = empty_to_none(elem_cnt_min)
    elem_cnt_max = empty_to_none(elem_cnt_max)

    
    wl_max = empty_to_none(wl_max)
    skip = empty_to_none(skip)
    limit = empty_to_none(limit)
    # output_file = empty_to_none(output_file)  # Uncomment if using output_file

    # Handle boolean parameters that may come as empty strings
    keyspace = empty_to_false(keyspace)
    wl_dist_len = empty_to_false(wl_dist_len)
    dupe_check_disable = empty_to_false(dupe_check_disable)
    save_pos_disable = empty_to_false(save_pos_disable)
    case_permute = empty_to_false(case_permute)

    for item in [prince_wordlist]:
        if item != None and os.path.exists(item) is False:
            message = f'file path {item} does not exist'
            return reply_bad_request(message)
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
        print ('running command')
        print (prince_command)
    except Exception as e:
        return reply_server_error(str(e))
    try:
        filename = generate_unique_filename(prince_wordlist_folder)
        prince_wordlist_file = os.path.join(prince_wordlist_folder,filename)
        prince_command.append('>')
        prince_command.append(prince_wordlist_file)
        process = subprocess.run(' '.join(prince_command),
                                    capture_output=True,
                                    cwd="hashcat",  
                                    shell=True, 
                                    text=True,
                                    encoding = 'utf-8')

        stderr = process.stderr
        if stderr:
            return reply_bad_request(stderr)
        path = f"http://{host_ip}:{port_num}/static/prince_wordlist_output/{filename}"
        message = "Result saved successfully."
        data= reply_success(message, path)
    except Exception as e:
        data= reply_server_error(str(e))
    return data
                            



@router.post("/prince-hashcat/")
async def prince_hashcat(    
    prince_wordlist: str = Form(...),   # prince wordlist
    # keyspace: bool = Form(False),         # Calculate number of combinations
    pw_min: str = Form(None),           # Prstr candidate if length is greater than NUM
    pw_max: str = Form(None),           # Prstr candidate if length is smaller than NUM
    elem_cnt_min: str = Form(None),     # Minimum number of elements per chain
    elem_cnt_max: str = Form(None),     # Maximum number of elements per chain
    # wl_dist_len: bool = Form(False),  # Calculate output length distribution from wordlist
    wl_max: str = Form(None),           # Load only NUM words from input wordlist or use 0 to disable
    dupe_check_disable: bool = Form(False), # Disable dupes check for faster initial load
    save_pos_disable: bool = Form(False),   # Save the position for later resume with -s
    skip: str = Form(None),             # Skip NUM passwords from start (for distributed)
    limit: str = Form(...),            # Limit output to NUM passwords (for distributed)
    # output_file: str = Form(None),    # Output-file
    case_permute: bool = Form(False),    # For each word in the wordlist that begins with a letter
                                        # generate a word with the opposite case of the first letter
    hash_file: str = Form(...), 
    hashcat_hash_code: str = Form(...),
    # wordlist: str = Form(...), 
    attack_mode: str = Form(None),
    rule_path: str = Form(None),
):
    hash_type = hashcat_hash_code
    if not os.path.exists(prince_wordlist):
        message = f"file_path {prince_wordlist} does not exist"
        return reply_bad_request(message = message)
    
    if attack_mode == None:
        message = "please provide attack_mode"
        return reply_bad_request (message)
    
    # Convert empty strings to None for optional string parameters
    rule_path = empty_to_none(rule_path)
    # Handle integer parameters that may come as empty strings
    pw_min = parse_int(pw_min)
    pw_max = parse_int(pw_max)
    elem_cnt_min = parse_int(elem_cnt_min)
    elem_cnt_max = parse_int(elem_cnt_max)
    wl_max = parse_int(wl_max)
    skip = parse_int(skip)
    limit = parse_int(limit)  # Since limit is required, ensure it's an integer

    # Handle boolean parameters that may come as empty strings
    dupe_check_disable = empty_to_false(dupe_check_disable)
    save_pos_disable = empty_to_false(save_pos_disable)
    case_permute = empty_to_false(case_permute)
    for item in [hash_file, rule_path]:
        if item != None and os.path.exists(item) is False:
            message = f'file path {item} does not exist'
            return reply_bad_request (message)

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
       return reply_server_error(str(e))

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
        process = subprocess.run(' '.join(full_command),
                                    capture_output=True,
                                    cwd="hashcat",  
                                    shell=True, 
                                    text=True,
                                    encoding = 'utf-8')

        stderr = process.stderr

        if stderr:
            message = str(stderr)
            return reply_bad_request(message)


        # Giao tiếp với tiến trình con
        full_command.append('--show')
        process = subprocess.run(' '.join(full_command),
                                    capture_output=True,
                                    cwd="hashcat",  
                                    shell=True, 
                                    text=True,
                                    encoding = 'utf-8')

        stderr = process.stderr
        stdout = process.stdout
    
        if stderr:
            message = str(stderr)
            return reply_bad_request(message)

        if stdout == '' or stdout == None:
            message = "Wordlist Exhausted. Cannot crack hash. Maybe find more wordlists"
            return reply_success(message, None)

        with open(cracked_hash_result_file, 'w') as f:
            f.writelines(stdout)
        with open(crack_collection, 'a') as f:
            f.writelines(stdout)
        # crack_collection_url = crack_collection.split("static",1)[1]
        # crack_collection_url = '/static' + crack_collection_url
        url = f"http://{host_ip}:{port_num}/static/cracked_hash/{filename}"
        # bonus_path = f"http://{host_ip}:{port_num}{crack_collection_url}" # potfile path
        message = "Result saved successfully"
        return reply_success(message = message, 
                             result = {"path":os.path.join(cracked_hash_result_folder, filename),
                                       "url":url})

    except Exception as e:
        return reply_server_error(e)
