import subprocess
def execute_command(command):
    """Execute the given command and return stdout, stderr."""
    result = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = result.communicate()
    return stdout, stderr

def handle_stdout(stdout, path, extract_hash_result_file):
        with open (extract_hash_result_file, 'w') as f :
            f.write(stdout)
        return {        
            "message": "Result saved successfully.", 
            "data": {"url":path}
            }   


def handle_stderr(stderr):
        zip_err_1 = 'compressed length of AES entry too short'
        zip_err_2 = 'not encrypted, or stored with non-handled compression type'
        if zip_err_1 in stderr or zip_err_2 in stderr:
            detail="Errors: zip file contains file that is empty/ have no data in it or the file is corrupted."
            return detail
        else:
            detail=f"Errors: {stderr}"
            return detail
