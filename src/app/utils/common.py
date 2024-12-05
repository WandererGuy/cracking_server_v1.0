import uuid
import os
from routers.model import MyHTTPException
# change this varibale require change gen_extract_command function too 

support_file_type = ['BitLocker', '7-Zip', 'WinZip', 'RAR5']

def gen_extract_command(hash_type, file_path):
    match hash_type:
        case "BitLocker":
            command = [
                'bitlocker2john',
                '-i',
                file_path
            ]
            
        case "7-Zip":
            command = [
                '7z2john',
                file_path
            ]        
        case "WinZip":
            command = [
                'zip2john',
                file_path
            ]
        case "RAR5":
            command = [
                'rar2john',
                file_path
            ]
        case _:
            return "Default case"
    return command


def empty_to_none(value):
    return None if value == '' else value

def empty_to_false(value):
    if value in (None, '', 'false', 'False', '0'):
        return False
    elif value in ('true', 'True', '1'):
        return True
        
    return bool(value)

def parse_int(value):
    value = empty_to_none(value)
    try:
        return int(value) if value is not None else None
    except Exception as e:
        message = 'please make sure all numbers are numbers not text '
        raise MyHTTPException(status_code=400, message=message)


# hash_type_dict = {
#     'MD5': 0,
#     'BitLocker': 22100,
#     '7-Zip': 11600,
#     'WinZip': 13600,
#     'RAR5': 13000
# }    
hash_type_dict = {
    '0': 0,
    '22100': 22100,
    '11600': 11600,
    '13600': 13600,
    '13000': 13000
}    

attack_mode_dict = {
    "Straight": 0,
    "Combination": 1,
    "Brute-force": 3,
    "Hybrid Wordlist + Mask": 6,
    "Hybrid Mask + Wordlist": 7,
    "Association": 9
}

def check_value_in_dict(value_to_check, dict):
    if value_to_check in dict.keys():
        return True
    else:
        available_keys = ', '.join(map(str, dict.keys()))
        detail=f"{value_to_check} does not exist in the dictionary keys. Available keys: {available_keys}"
        return detail 

def check_value_in_list(value_to_check, ls):
    if value_to_check in ls:
        return True
    else:
        available_keys = ', '.join(map(str, ls))
        detail=f"{value_to_check} does not exist in the dictionary keys. Available keys: {available_keys}"
        return detail 

def list_value_in_dict(support_file_type_list):
        s = ''
        for i in support_file_type_list:
            s += i + ', '
        return s



def data_type_translate(data_name):
    # return hash_type_dict[data_name]
    return data_name
def attack_mode_translate(attack_mode):
    return attack_mode_dict[attack_mode]   
 
def clean_path (path):
    # if path != None and path != '':
    #     path = '/mnt/'+ path
    #     path = path.replace('D:', 'd').replace('C:','c').replace('E:','e').replace('F:','f').replace('\\', '/')
    return path

# def refine_hash (hash_type, hash):
    # match hash_type:
    #     case 22100:
    #         command = [
    #             'bitlocker2john',
                
    #         ]
    #         return "Handled case one"
def clean_path_v2 (path):     
    path = path.replace('\\\\', '/')   
    return path.replace ('\\', '/')
def generate_unique_filename(UPLOAD_FOLDER, extension="txt"):
    if extension != None:
        filename = f"{uuid.uuid4()}.{extension}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            return filename
    else:
        filename = f"{uuid.uuid4()}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            return filename 
        
def check_result_available(file):
    with open (file, 'r') as f_:
        f = f_.read()
        if 'Status...........: Exhausted' in f:
            return False
        else:
            return True