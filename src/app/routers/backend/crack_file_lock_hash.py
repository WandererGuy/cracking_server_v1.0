from fastapi import Form, APIRouter
import os 
from routers.model import reply_bad_request
from utils.frontend_validation import is_utf8, target_input_validation
from utils.common import empty_to_none

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(script_dir))
config_path = os.path.join(parent_dir,'config.ini')


support_file_type = ['BitLocker', '7-Zip', 'WinZip', 'RAR5']
router = APIRouter()

@router.post("/backend-crack-file-lock-hash/")
async def backend_crack_file_lock_hash(
    file_lock_path: str = Form(None),
    file_lock_type: str = Form(None),
    additional_wordlist: str = Form(None),
    full_name: str = Form(None),
    birth: str = Form(None),
    email: str = Form(None),
    account_name: str = Form(None),
    id_num: str = Form(None),
    phone: str = Form(None),
    other_keywords: str = Form(None),
    ):
    MAX_MASK_GENERATE_WORDLIST = 1000000000000 # max mask number to create wordlist
    MAX_MASK_GENERATE_MASKLIST = 80 # max mask number to bruteforce
    # can only achieve max mask if all information is provided 

    if file_lock_type not in support_file_type: 
        return reply_bad_request(message = f"Unsupported file type '{file_lock_type}'\
                                            . Support file type: {support_file_type}")

    file_info = {
        "file_lock_path": file_lock_path,
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

    if file_info['file_lock_path'] == None: 
        return reply_bad_request(message = "No file input given")
    if not os.path.exists(file_info['file_lock_path']): 
        return reply_bad_request(message = f"{file_lock_path} not found")
    if file_info['additional_wordlist'] != None:
        if not os.path.exists(file_info['additional_wordlist']): 
            return reply_bad_request(message = f"{additional_wordlist} not found")
    
    target_input_validation(target_info)


