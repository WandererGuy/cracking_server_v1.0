import uuid
import os

support_file_type = ['BitLocker', '7-Zip', 'WinZip', 'RAR5']

hash_type_dict = {
    'MD5': 0,
    'BitLocker': 22100,
    '7-Zip': 11600,
    'WinZip': 13600,
    'RAR5': 13000
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

def gen_extract_command(hash_type, file_path):
    match hash_type:
        case 22100:
            command = [
                'bitlocker2john',
                file_path
            ]
            return "Handled case one"
        case 11600:
            command = [
                '7z2john',
                file_path
            ]        
        case 13600:
            command = [
                'zip2john',
                file_path
            ]
        case 13000:
            command = [
                'rar2john',
                file_path
            ]
        case _:
            return "Default case"
    return command


def data_type_translate(data_name):
    return hash_type_dict[data_name]

def attack_mode_translate(attack_mode):
    return attack_mode_dict[attack_mode]   
 
def clean_path (path):
    if path != None and path != '':
        path = '/mnt/'+ path
        path = path.replace('D:', 'd').replace('C:','c').replace('E:','e').replace('F:','f').replace('\\', '/')
    return path

# def refine_hash (hash_type, hash):
    # match hash_type:
    #     case 22100:
    #         command = [
    #             'bitlocker2john',
                
    #         ]
    #         return "Handled case one"
        

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