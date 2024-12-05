# import subprocess
# command = ['hashcat', 
#            r"C:\Users\Admin\CODE\work\PASSWORD_CRACK\cracking_server_v1.0\src\app\static\extract_hash_results\3ba0cc33-b5d9-4823-afe5-b7cfa408338a.txt",
#            ]
# result = subprocess.run(command,
#                             capture_output=True, 
#                             cwd="jtr/run",
#                             shell=True,
#                             text=True, 
#                             encoding='utf-8')
# print(result.stdout)
# path = r'C:\Users\Admin\CODE\work\PASSWORD_CRACK\cracking_server_v1.0\samples\full_output_sample\bitlocker_hash_full.txt'
# with open(path,'r') as f:
#     data = f.read()
#     t = data.split('User Password hash:')[1].split('Hash type: User Password with MAC verification')[0]
#     print (t)
import os 
path = 'C:\Users\Admin\Downloads\manhlol.txt'
# path = path.replace(' ', '\\ ')
# if os.path.exits(path):
#     print (path)