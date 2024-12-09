from utils.common import fix_path
from routers.model import reply_bad_request, reply_success

def write_to_remaining_hashfile(remaining_hash_file, uncracked_hashes):
    with open (remaining_hash_file, 'w', encoding = 'utf-8') as f:
        for hash in uncracked_hashes:
            f.write(f'{hash}\n')

def end_cracking(cracked_hashes, cracked_hash_file):
    with open (cracked_hash_file, 'w', encoding = 'utf-8') as f:
        for key, value in cracked_hashes.items():
            f.write(f'{key}:{value}\n\n\n')
    print ('written result in ', fix_path(cracked_hash_file))
    return reply_success(message = 'Successfully cracked ALL hashes', 
                            result = {"path_cracked_hash": fix_path(cracked_hash_file)}) 
