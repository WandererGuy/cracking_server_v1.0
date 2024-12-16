from fastapi import Form, APIRouter
import os 
import configparser
import subprocess
from utils.extract_hash import *
from utils.common import *
from routers.model import reply_bad_request, reply_success, reply_server_error


# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='fastapi.log', filemode='w')
# logger = logging.getLogger(__name__)

# Get the directory where the current script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to config.ini
parent_dir = os.path.dirname(script_dir)
config_path = os.path.join(parent_dir, 'config.ini')

# Read the config file
config = configparser.ConfigParser()
config.read(config_path)
host_ip = config['DEFAULT']['host'] 
port_num = config['DEFAULT']['port'] 
terminal_crack_warmup_time = int(config['DEFAULT']['terminal_crack_warmup_time'])
# Construct the path to config.ini
static_path = os.path.join(parent_dir,'static')

extract_hash_result_folder = os.path.join(static_path, "extract_hash_results")

router = APIRouter()
running_dir = os.getcwd()
fake_wordlist_path = os.path.join(running_dir, 'samples','wordlist','fake_test_hashcat_code.txt')
fake_potfile_path = os.path.join(running_dir, 'samples','wordlist','fake_test_potfile.pot')
temp_output = os.path.join(static_path,'hashcat_temp_output.txt')

hashcat_hash_code_dict = {
    "": ["0"],  
    "$zip2$": ['13600'],
    "$pkzip2$": ['17200', '17210', '17220', '17225', '17230'],
    "$rar5$": ['13000'],
    "$bitlocker$": ['22100'],
    "$7z$": ['11600']
}
def kill_process(process):
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill() 

import time 
def test_hashcat_hash_code(extract_hash_result_file, hashcat_hash_code):
    command = ["hashcat"]    
    command.append(extract_hash_result_file)
    command.append(fake_wordlist_path)
    command.append('-a')
    command.append('0')
    command.append('-m')
    command.append(hashcat_hash_code)
    command.append('--potfile-path')
    command.append(fake_potfile_path)
    command.append('--backend-ignore-opencl')
    cm = " ".join(command)
    print ('fake test hashcat_hash_code: ')
    print (cm)
    error_flag = False
    exhausted_flag = False
    with subprocess.Popen(command, 
                        cwd="hashcat", 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, 
                        text=True, 
                        shell=True,
                        encoding='utf-8') as process:
        # Read and print output line by line as it comes
        time.sleep(terminal_crack_warmup_time)
        for line in process.stdout:
            print(line, end='')  # Print the output in real-time
            for error in ["No hashes loaded", "Token length exception", "Separator unmatched"]:
                if error in line:
                    error_flag = True
                    # if last_item: kill_process(process)
                    # return False, error
            if 'Exhausted' in line:
                    exhausted_flag = True
                    # if last_item: kill_process(process)
                    # return True, None
    # kill_process(process)
    # if last_item: kill_process(process)
    if exhausted_flag: return True, None
    if error_flag: return False, error
    return False, 'first recorded error'
def find_hashcat_hash_code(extract_hash_result_file, real_hash):
    '''
    extract_hash_result_file : hash file have 1 hash 
    real_hash : hash in the hash file
    why not pass hash directly?  because hash can be too long and cannot be passed directly
    so hash file have better control
    '''
    for key, value in hashcat_hash_code_dict.items():
        if key in real_hash:

            for hashcat_hash_code in value:
                valid_code, error = test_hashcat_hash_code(extract_hash_result_file, hashcat_hash_code)
                if valid_code is False: continue
                else: return hashcat_hash_code
            # break # since unique type only found once 
    return None

def find_hash(file_type, stdout):
    # real_hash = None
    print ('------------------ file_type ------------------')
    print (file_type)
    if file_type == "RAR5":
        border = ':'
        real_hash = stdout.split(border)[1]
        return real_hash
    elif file_type == "WinZip":
        check = "$zip2$"
        if check in stdout:
            real_hash = stdout.split(check, 1)[1]
            check_2 = "zip2$"
            real_hash = check + real_hash.split(check_2, 1)[0] + check_2
            return real_hash

        check = "$pkzip2$"
        if check in stdout:
            real_hash = stdout.split(check, 1)[1]
            check_2 = "pkzip2$"
            real_hash = check + real_hash.split(check_2, 1)[0] + check_2
            return real_hash
    elif file_type == "BitLocker":
        check = "User Password hash:"
        if check in stdout:
            real_hash = stdout.split(check, 1)[1]
            check_2 = "$bitlocker$"
            real_hash = stdout.split(check_2, 1)[1]
            check_3 = "Hash type: User Password with MAC verification"
            real_hash = check_2 + real_hash.split(check_3, 1)[0]
            real_hash = real_hash.strip('\n')
            return real_hash
    elif file_type == "7-Zip":
        border = ':'
        real_hash = stdout.split(border)[1]
        return real_hash
    else: return None

import pandas as pd
def session_save(session_folder_path, hash_file, res):
    excel_path = os.path.join(session_folder_path, 'session.xlsx')
    df = pd.read_excel(excel_path)
    os.makedirs(session_folder_path, exist_ok=True)
    for hash, hashcat_hash_code in res.items():
        name_single_hash_file = str(uuid.uuid4()) + '.txt'
        folder_1 = os.path.join(session_folder_path, hashcat_hash_code)
        file_1 = os.path.join(folder_1, name_single_hash_file)
        all_same_hashcat_hash_code_file = os.path.join(folder_1, 'all.txt')
        os.makedirs(file_1, exist_ok=True)
        with open(file_1, 'w') as f:
            f.write(hash)
        with open(all_same_hashcat_hash_code_file, 'a') as f:
            f.write(hash)
            f.write('\n')
        new_row = {
                'hash value in file': file_1, 
                'original extracted file path': hash_file, 
                'original hash file path': "", 
                'hashcat hash code': hashcat_hash_code, 
                'hashes same hashcat hash code in file': all_same_hashcat_hash_code_file, 
                'plaintext password': ""
                }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(excel_path, index=False)


@router.post ("/extract-hash") 
async def extract_hash(  
    session_name: str = Form(...),  
    file_type: str = Form(...),
    file_path: str = Form(...)
    ):
    
    if not os.path.exists(file_path):
        message = f"file_path {fix_path(file_path)} does not exist"
        return reply_bad_request(message = message)



    """
    Description:<br>
    this endpoint used to extract hash(es) from locked/encrypted file with password<br>
    <br>
    Input: <br>
    file_type : type of file be extracted<br>
    supported file type in support_file_type: MD5, BitLocker, 7-Zip, WinZip, RAR<br> 
    file_path : path to file to be extracted<br>
    Expected response :<br>
    url to file txt with hash extracted 
    """
    detail = check_value_in_list(file_type, support_file_type)
    if detail is not True:
       message = detail
       return reply_bad_request(message)
        
    filename = generate_unique_filename(extract_hash_result_folder)
    extract_hash_result_file = os.path.join(extract_hash_result_folder, filename)

    command = gen_extract_command(file_type, fix_path(file_path))
    print ('running command')
    print (" ".join(command))
    try:
        stdout, stderr = execute_command(command)
        if stderr:
            detail = handle_stderr(stderr)
            if 'No such file or directory' in detail:
                return reply_bad_request(detail)
        if stdout == None or stdout == "":
            detail = "Cannot extract file. Maybe: wrong file type OR no hash information found in file OR file is too small/ nearly empty"
            return reply_bad_request(detail)

        real_hash = find_hash(file_type, stdout)
        if real_hash == None:
            detail = "Cannot extract hash from stdout, hash have not yet supported by system"
            return reply_bad_request(detail)

        with open(extract_hash_result_file, 'w') as f:
            f.write(real_hash)
        print ('---------written in---------')
        print(extract_hash_result_file)
        print ('')
        hashcat_hash_code = find_hashcat_hash_code(extract_hash_result_file, real_hash)
        if hashcat_hash_code == None:
            message = "Cannot find hashcat hash_code for the hash. Maybe hash extracted wrong or not hash not supported by hashcat"
            return reply_bad_request(message)
        path = f"http://{host_ip}:{port_num}/static/extract_hash_results/{filename}"
        # result =  {
        #         "path": fix_path(extract_hash_result_file), 
        #         "url": path,
        #         "hashcat_hash_code": hashcat_hash_code
        #          }
        result = None
        message = "Result saved successfully"
        session_folder_path = os.path.join(static_path, 'session', session_name)
        session_save(session_folder_path, fix_path(file_path), {real_hash:hashcat_hash_code})
        return reply_success(message, result)
    except Exception as e:
        return reply_server_error(e)





