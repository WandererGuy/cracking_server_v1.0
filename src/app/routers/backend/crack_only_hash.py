from fastapi import Form, APIRouter
import os 
import uuid
from utils.common import fix_path, handle_response
from routers.model import reply_bad_request, reply_success
from utils.frontend_validation import is_utf8, target_input_validation
from utils.common import empty_to_none
from utils.validate_hashfile import validate_hashfile_request, ls_support_hashcat_hash_code
from utils.backend.targuess import targuess_generate
from utils.backend.hashcat import use_hashcat, handle_hashcat_response
from utils.backend.write_hashfile import write_to_remaining_hashfile, end_cracking
import time 

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(script_dir))
config_path = os.path.join(parent_dir,'config.ini')


import configparser
config = configparser.ConfigParser()
config.read(config_path)

host_ip = config['DEFAULT']['host'] 
TARGUESS_PORT_NUM = config['DEFAULT']['TARGUESS_PORT_NUM'] 
CRACKING_SERVER_PORT_NUM = config['DEFAULT']['CRACKING_SERVER_PORT_NUM'] 
TARGUESS_TRAIN_RESULT_REFINED_PATH = config['DEFAULT']['TARGUESS_TRAIN_RESULT_REFINED_PATH'] 
PORT_BACKEND = config['DEFAULT']['PORT_BACKEND']
HASH_CRACK_URL = f"http://{host_ip}:{CRACKING_SERVER_PORT_NUM}/hash-crack/"
TARGUESS_URL_WORDLIST = f"http://{host_ip}:{TARGUESS_PORT_NUM}/generate-target-wordlist/"
TARGUESS_URL_MASKLIST = f"http://{host_ip}:{TARGUESS_PORT_NUM}/generate-target-mask-list/"
VALIDATE_HASHFILE_URL = f"http://{host_ip}:{CRACKING_SERVER_PORT_NUM}/validate-hashfile/"

router = APIRouter()
static_path = os.path.join(parent_dir,'static')
hash_dump_folder = os.path.join(static_path,'backend','hash_dump')

backend_temp_output = os.path.join(static_path,'backend_temp_output.txt')
hashcat_temp_output = os.path.join(static_path,'hashcat_temp_output.txt')
backend_temp_step = os.path.join(static_path,'backend_temp_step.txt')

remaining_hash_path = os.path.join(static_path, 'backend', 'remaining_hash')
cracked_hash_path = os.path.join(static_path, 'backend', 'cracked_hash')

def write_backend_step(content):
    with open(backend_temp_step, 'w', encoding='utf-8') as f:
        f.write(content)
            
@router.post("/backend-crack-only-hash/")
async def backend_crack_only_hash(
    hash_file: str = Form(...),
    hashcat_hash_code: str = Form(None),
    additional_wordlist: str = Form(None),
    full_name: str = Form(None),
    birth: str = Form(None),
    email: str = Form(None),
    account_name: str = Form(None),
    id_num: str = Form(None),
    phone: str = Form(None),
    other_keywords: str = Form(None),
    ):
    write_backend_step(content = 'VALIDATING USER INPUT')
    url_cracked_hash = f"http://{host_ip}:{PORT_BACKEND}/static/backend/cracked_hash/"

    MAX_MASK_GENERATE_WORDLIST = 1000000000000 # max mask number to create wordlist
    MAX_MASK_GENERATE_MASKLIST = 80 # max mask number to bruteforce
    # can only achieve max mask if all information is provided 

    if hashcat_hash_code not in ls_support_hashcat_hash_code: 
        return reply_bad_request(message = f"Unsupported hashcat_hash_code '{hashcat_hash_code}' \
                                 . Support hash type: {ls_support_hashcat_hash_code}")
    
    uncracked_hashes = []
    cracked_hashes = {}
    remaining_hash_file = os.path.join(remaining_hash_path, str(uuid.uuid4()) + '.txt')
    cracked_hash_file = os.path.join(cracked_hash_path, str(uuid.uuid4()) + '.txt')
    print ('choose remaining hash file: ', remaining_hash_file)
    print ('choose cracked hash file: ', cracked_hash_file)

    file_info = {
        "hash_file": hash_file,
        "additional_wordlist": additional_wordlist
    }
    target_info = {
        "full_name": full_name,
        "birth": birth,
        "email": email,
        "account_name": account_name,
        "id_num": id_num,
        "phone": phone,
        "other": other_keywords
    }
    # standardize input 
    for key, value in file_info.items():
        file_info[key] = empty_to_none(value)
    for key, value in target_info.items():
        target_info[key] = empty_to_none(value)
        if target_info[key] != None:
            is_utf8(target_info[key])

    target_input_validation(target_info)


    if file_info['hash_file'] == None: 
        return reply_bad_request(message = "No hash file input given")
    if not os.path.exists(file_info['hash_file']): 
        return reply_bad_request(message = f"{fix_path(hash_file)} , directory is not found")
    if file_info['additional_wordlist'] != None:
        if not os.path.exists(file_info['additional_wordlist']): 
            return reply_bad_request(message = f"{fix_path(additional_wordlist)} , directory is not found")
    
    print ('------------------ VALIDATING HASH FILE ------------------')
    res = handle_response(validate_hashfile_request(hash_file, 
                      hashcat_hash_code, 
                      hash_dump_folder, 
                      VALIDATE_HASHFILE_URL))
    message = res["message"]
    valid = res["result"]
    if valid == "empty":
        return reply_bad_request(message = 
                        'hash file is empty. \
                        Please add hash to the hash file.')
    if valid == False:
        return reply_bad_request(message = message)
    print ('------------------ hashfile is valid ------------------')

    with open (file_info['hash_file'], 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
        for hash in lines:
            hash = hash.strip('\n').strip()
            uncracked_hashes.append(hash)

    uncracked_hashes = list(set(uncracked_hashes))


    # start working 
    # targuess wordlist
    write_backend_step(content = 'GENERATING TARGUESS WORDLIST')
    res = targuess_generate(targuess_train_result_refined_path = TARGUESS_TRAIN_RESULT_REFINED_PATH,
                            targuess_url = TARGUESS_URL_WORDLIST, 
                            target_info = target_info, 
                            max_mask_generate = MAX_MASK_GENERATE_WORDLIST)
    print ('------------------ receive response from targuess ------------------')
    print (res.json())
    json_res = handle_response(res)
    print ('------------------ ATTEMP WITH TARGUESS WORDLIST (NO RULE) ------------------')
    write_backend_step(content = 'CRACKING HASH WITH TARGET WORDLIST (NO RULE)')
    WORDLIST_FILE_TARGUESS = fix_path(json_res['result']['path'])
    time.sleep(4) # for targuess
    hashcat_material = {
        "hash_file": file_info['hash_file'],
        "wordlist_file": WORDLIST_FILE_TARGUESS,
        "hashcat_hash_code": hashcat_hash_code,
        "rule_path": '',
        "gpu_number": '' # for now consider 1 is fastest 
    }
    print ('hashcat material: ', hashcat_material)
    res = use_hashcat(hashcat_material, HASH_CRACK_URL)  
    hash_dict = handle_hashcat_response(res)
    if hash_dict != None:
        for key, value in hash_dict.items():
            uncracked_hashes.remove(key)
            cracked_hashes[key] = value
    write_to_remaining_hashfile(remaining_hash_file, uncracked_hashes)
    if uncracked_hashes == []:
        return end_cracking(cracked_hashes, cracked_hash_file, url_cracked_hash)

    print ('------------------ ATTEMP WITH TRAWLING WORDLIST (NO RULE) ------------------')
    write_backend_step(content = 'CRACKING HASH WITH TRAWLING WORDLIST (NO RULE)')
    # trawling wordlist < 1GB 
    WORDLIST_FILE_TRAWLING = os.path.join(os.getcwd(),'wordlist_samples','zing_tailieuvn_smallwordlist.txt')
    # WORDLIST_FILE_TRAWLING = os.path.join(os.getcwd(), 'samples', 'wordlist','fake.txt')

    hashcat_material = {
        "hash_file": remaining_hash_file,
        "wordlist_file": WORDLIST_FILE_TRAWLING,
        "hashcat_hash_code": hashcat_hash_code,
        "rule_path": '',
        "gpu_number": ''
    }
    res = use_hashcat(hashcat_material, HASH_CRACK_URL)  
    hash_dict = handle_hashcat_response(res)
    if hash_dict != None:
        for key, value in hash_dict.items():
            uncracked_hashes.remove(key)
            cracked_hashes[key] = value
    write_to_remaining_hashfile(remaining_hash_file, uncracked_hashes)
    if uncracked_hashes == []:
        return end_cracking(cracked_hashes, cracked_hash_file, url_cracked_hash)


    print ('------------------ ATTEMP WITH TARGUESS WORDLIST (WITH RULE) ------------------')
    write_backend_step(content = 'CRACKING HASH WITH TARGET WORDLIST (WITH RULE)')

    rule_path = os.path.join(os.getcwd(),'samples','rule_sample','OneRuleToRuleThemAll.rule')
    hashcat_material = {
        "hash_file": remaining_hash_file,
        "wordlist_file": WORDLIST_FILE_TARGUESS,
        "hashcat_hash_code": hashcat_hash_code,
        "rule_path": rule_path,
        "gpu_number": ''
    }
    res = use_hashcat(hashcat_material, HASH_CRACK_URL)  
    hash_dict = handle_hashcat_response(res)
    if hash_dict != None:
        for key, value in hash_dict.items():
            uncracked_hashes.remove(key)
            cracked_hashes[key] = value
    write_to_remaining_hashfile(remaining_hash_file, uncracked_hashes)
    if uncracked_hashes == []:
        return end_cracking(cracked_hashes, cracked_hash_file, url_cracked_hash)



    print ('------------------ ATTEMP WITH MY TRAWLING WORDLIST (WITH RULE) ------------------')
    write_backend_step(content = 'CRACKING HASH WITH TRAWLING WORDLIST (WITH RULE)')
    rule_path = os.path.join(os.getcwd(),'samples','rule_sample','OneRuleToRuleThemAll.rule')
    hashcat_material = {
        "hash_file": remaining_hash_file,
        "wordlist_file": WORDLIST_FILE_TRAWLING,
        "hashcat_hash_code": hashcat_hash_code,
        "rule_path": rule_path,
        "gpu_number": ''
    }
    res = use_hashcat(hashcat_material, HASH_CRACK_URL)  
    hash_dict = handle_hashcat_response(res)
    if hash_dict != None:
        for key, value in hash_dict.items():
            uncracked_hashes.remove(key)
            cracked_hashes[key] = value
    write_to_remaining_hashfile(remaining_hash_file, uncracked_hashes)


    if cracked_hashes != {}:
        if uncracked_hashes == []:
            return end_cracking(cracked_hashes, cracked_hash_file, url_cracked_hash)


        else:
            res = end_cracking(cracked_hashes, cracked_hash_file, url_cracked_hash)
            res["message"] = 'Successfully cracked these hashes'
            res["result"]["path_remain_hash"] = fix_path(remaining_hash_file)
            filename = os.path.basename(res["result"]["path_remain_hash"])
            res["result"]["url_remain_hash"] = f"http://{host_ip}:{PORT_BACKEND}/static/backend/remaining_hash/{filename}"
            return res 
    else:
        return reply_success(message = 'No hash was cracked', result = None)

    # res = targuess_generate(targuess_train_result_refined_path = TARGUESS_TRAIN_RESULT_REFINED_PATH,
    #                         targuess_url = TARGUESS_URL_MASKLIST, 
    #                         target_info = target_info, 
    #                         max_mask_generate = MAX_MASK_GENERATE_MASKLIST)
    # return handle_response(res)
