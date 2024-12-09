import requests
from utils.common import fix_path, handle_response
from routers.model import MyHTTPException
def send_hash_crack(url = '', 
                    hash_file = '',
                    wordlist_file = '', 
                    hashcat_hash_code = '', 
                    attack_mode = '', 
                    rule_path = '', 
                    restore = '',
                    runtime = '',
                    status = '',
                    status_json = '',
                    status_timer = '',
                    gpu_number = ''):
    payload = {'hash_file': hash_file,
    'wordlist_file': wordlist_file,
    'hashcat_hash_code': hashcat_hash_code,
    'attack_mode': attack_mode,
    'rule_path': rule_path,
    'restore': restore,
    'runtime': runtime,
    'status': status,
    'status_json': status_json,
    'status_timer': status_timer,
    'gpu_number': gpu_number}
    files=[]
    headers = {}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    return response



def use_hashcat(hashcat_material: dict, HASH_CRACK_URL):
    # hash_file = 'C:/Users/Admin/CODE/work/PASSWORD_CRACK/cracking_server_v1.0/src/app/static/extract_hash_results/736915d8-d26f-4c19-a45d-2a03503b74e1.txt'
    # wordlist_file = 'C:\\Users\\Admin\\CODE\\work\\PASSWORD_CRACK\\cracking_server_v1.0\\wordlist_samples\\zing_tailieuvn_smallwordlist.txt'
    # hashcat_hash_code = '13000'
    attack_mode = 'Straight'
    status = True
    status_timer = 5

    res = send_hash_crack(url = HASH_CRACK_URL,
                               hash_file = hashcat_material['hash_file'],
                               wordlist_file = hashcat_material['wordlist_file'],
                               hashcat_hash_code = hashcat_material['hashcat_hash_code'],
                               attack_mode = attack_mode,
                               rule_path = hashcat_material['rule_path'],
                               status = status,
                               status_timer = status_timer,
                               gpu_number = hashcat_material['gpu_number'])
    
    return res 

def handle_hashcat_response(res):
    t = handle_response(res)
    hash_dict = {}
    print ('hashcat response')
    print (t)
    if t['status_code'] == 200:
        if 'Wordlist Exhausted' not in t['message']:
            cracked_path = t['result']['path']
            cracked_path = fix_path(cracked_path)
            with open(cracked_path, 'r', encoding = 'utf-8') as f:
                data = f.readlines()
                for line in data:
                    line = line.strip('\n').strip()
                    hash = line.split(':')[0]
                    plaintext = line.split(':')[1]
                    hash_dict[hash] = plaintext
                    print ('------------------ CRACKED HASH :) ------------------')
                    print (hash)
            return hash_dict
        else:
            print ('------------------ NO CRACKED HASH :( ------------------')
            return None
    else:
        raise MyHTTPException(status_code=t['status_code'], message = t['message'])
