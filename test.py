# import socket
# import configparser

# # Function to get the local IP address
# def get_local_ip():
#     # Get the local machine's hostname
#     hostname = socket.gethostname()
#     # Resolve the IP address of the local machine
#     local_ip = socket.gethostbyname(hostname)
#     return local_ip

# # Define the path to your config.ini file
# config_file = 'config.ini'

# # Get the local IP address dynamically
# new_ip = get_local_ip()

# # Initialize the configparser
# config = configparser.ConfigParser()

# # Read the current configuration file
# config.read(config_file)

# # Modify the 'host' value in the appropriate section
# config.set('DEFAULT', 'host', new_ip)

# # Write the updated configuration back to the file
# with open(config_file, 'w') as configfile:
#     config.write(configfile)

# print(f"Host IP address dynamically updated to: {new_ip}")

# path = r'C:\Users\Admin\CODE\work\PASSWORD_CRACK\cracking_server_v1.0\samples\rule_sample\OneRuleToRuleThemAll.rule'

# with open(path,'r', encoding='utf-8', errors='ignore') as f:
#     lines = f.readlines()
#     for index, line in enumerate(lines):

#         if line == 'c\n':
#             print (index)
import os 
path = r'C:\Users\Admin\CODE\work\PASSWORD_CRACK\cracking_server_v1.0\samples\rule_sample\Extreme_Breach_Masks\trawling'
name = 'all_Extreme_Breach_Masks_trawling_mask.hcmask'
final_path = os.path.join(path, name)
final_ls = []
print ('gayyy')
for filename in sorted(os.listdir(path)):
    if 'Extreme_Breach_Masks' in filename:
        continue
    print (filename)
    full_path = os.path.join(path, filename)
    with open(full_path,'r', encoding='utf-8', errors='ignore') as f:
        lines = f.read()
        final_ls.append(lines)

with open(final_path,'w', encoding='utf-8') as f:
    for item in final_ls:
        f.write(item)
        f.write('\n')
        f.write('\n')
    
