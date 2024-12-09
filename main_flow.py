import requests 
import os 
import time 
import sys

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

def handle_response(response):
    # Check if the response is in JSON format
    if response.status_code == 200:  # Check if the request was successful
        try:
            json_data = response.json()  # Parse the JSON response
            return json_data  # Print the parsed JSON
        except ValueError:
            print("Response is not valid JSON")
    else:
        print(f"Request failed with status code {response.status_code}")
    sys.exit()

if __name__ == "__main__":

    url = "http://192.168.1.5:8010/hash-crack"
    hash_file = 'C:/Users/Admin/CODE/work/PASSWORD_CRACK/cracking_server_v1.0/src/app/static/extract_hash_results/736915d8-d26f-4c19-a45d-2a03503b74e1.txt'
    wordlist_file = 'C:\\Users\\Admin\\CODE\\work\\PASSWORD_CRACK\\cracking_server_v1.0\\wordlist_samples\\zing_tailieuvn_smallwordlist.txt'
    hashcat_hash_code = '13000'
    attack_mode = 'Straight'
    gpu_number = 2
    status = True

    response = send_hash_crack(url = url,
                               hash_file = hash_file,
                               wordlist_file = wordlist_file,
                               hashcat_hash_code = hashcat_hash_code,
                               attack_mode = attack_mode,
                               status = status,
                               status_timer = 5,
                               gpu_number = gpu_number)
    res = handle_response(response)

    rule_path = r'C:\Users\Admin\CODE\work\PASSWORD_CRACK\cracking_server_v1.0\samples\rule_sample\OneRuleToRuleThemAll.rule'
    response = send_hash_crack(url = url,
                               hash_file = hash_file,
                               wordlist_file = wordlist_file,
                               hashcat_hash_code = hashcat_hash_code,
                               attack_mode = attack_mode,
                               rule_path = rule_path,
                               status = status,
                               status_timer = 5,
                               gpu_number = gpu_number)
    res = handle_response(response)
    

