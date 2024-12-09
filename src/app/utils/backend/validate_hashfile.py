from routers.extract_hash import test_hashcat_hash_code
from routers.model import MyHTTPException
import sys
import requests
import os 
from utils.common import fix_path
hash_type_to_hashcat_hash_code_dict = {
    "BitLocker": ['22100'],
    "7-Zip": ['11600'],
    "WinZip": ['13600','17200', '17210', '17220', '17225', '17230'],
    "RAR5": ['13000'],
    "MD5": ['0']
}
support_hash_type = ['BitLocker', '7-Zip', 'WinZip', 'RAR5', 'MD5']

current_dir = os.path.dirname(os.path.abspath(__file__))
document_path = fix_path(os.path.join(current_dir, 'example_hashes[hashcat wiki].pdf'))

BONUS_MESSAGE = f'Also, please notice these 4 rules for your hash file: \
                1. keep each hash in one line, remove any space, \
                2. remove any \':\' from hash, \
                3. remove any file path from hash, \
                4. file can only have 1 type of hash.'
                


def hash_validate(hash, hash_type):
    hashcat_hash_code_ls=hash_type_to_hashcat_hash_code_dict[hash_type]
    for hashcat_hash_code in hashcat_hash_code_ls:
        value, error = test_hashcat_hash_code(hash, hashcat_hash_code)
        if  value != False: # success
            return hashcat_hash_code
    message = f'given hash \'{hash}\' have error \'{error}\' for hash type \'{hash_type}\', this error is in hashcat model. \
                Please fix the hash according to error OR remove the hash from file \
                For fixing error, you can find example hash example for each hash type in pdf file: {document_path} to compare your hash \
                Asking yourself if the hash need to be same length/same pattern to fix the error. \
                '
    message = message + BONUS_MESSAGE
    raise MyHTTPException(status_code=400, message = message)



def hashfile_validate(hash_file, hash_type):
    empty_file = True # make sure hash file not empty
    with open(hash_file, 'r') as f:
        hashes = f.readlines()
        for index, hash in enumerate(hashes):
            hash = hash.strip('\n').strip()
            if hash == '':
                continue
            empty_file = False
            hashcat_hash_code = hash_validate(hash, hash_type)
            # if index == 0:
            #     fix_hashcat_hash_code = hashcat_hash_code
            # else:
            #     if hashcat_hash_code != fix_hashcat_hash_code:
            #         raise MyHTTPException(status_code=400, message = 
            #                                f'hash "{hash}" is different type from hash from start of the file. \
            #                                Please fix or remove the hash. \
            #                                file can only have 1 type of hash. \
            #                                Please keep all hash the same type ')
    if empty_file == True:
        raise MyHTTPException(status_code=400, message = 
                               'hash file is empty. \
                               Please add hash to the hash file.')
    print ('hashfile is valid')
    return hashcat_hash_code
