from utils.server_utils import *
def gen_hashcat_command(
    hash_type: str ,
    hash_file: str , 
    # wordlist: str , 
    attack_mode: str,
    rule_path: str 
    ):

    # Check if the value exists in the dictionary keys
    check_value_in_dict(attack_mode, attack_mode_dict)
    check_value_in_dict(hash_type, hash_type_dict)     

    hash_type = str(data_type_translate(hash_type))
    hash_file = clean_path(hash_file)
    # wordlist = clean_path(wordlist)
    rule_path = clean_path(rule_path)
    attack_mode = str(attack_mode_translate(attack_mode))

    
    # Build the Hashcat command
    command = [
        'hashcat',
        '-m', hash_type,       # Hash type
        '-a', attack_mode,             # Attack mode
        hash_file,            # Hash
        # wordlist,               # Wordlist
    ]
    if rule_path != None and rule_path != '':
        command.append('-r')
        command.append(rule_path)
    return command

def genPrinceCommandNormal(
    prince_run_file=None,
    prince_wordlist=None,
    keyspace=None,
    pw_min=None,
    pw_max=None,
    elem_cnt_min=None,
    elem_cnt_max=None,
    wl_dist_len=None,
    wl_max=None,
    dupe_check_disable=None,
    save_pos_disable=None,
    skip=None,
    limit=None,
    output_file=None,
    case_permute=None
):

    # Convert strings to appropriate types
    # if keyspace is not None:
    #     keyspace = int(keyspace)
    if pw_min is not None:
        pw_min = int(pw_min)
    if pw_max is not None:
        pw_max = int(pw_max)
    if elem_cnt_min is not None:
        elem_cnt_min = int(elem_cnt_min)
    if elem_cnt_max is not None:
        elem_cnt_max = int(elem_cnt_max)
    # if wl_dist_len is not None:
    #     wl_dist_len = wl_dist_len in ["true", "1", "yes"]
    if wl_max is not None:
        wl_max = int(wl_max)
    # if dupe_check_disable is not None:
    #     dupe_check_disable = dupe_check_disable in ["true", "1", "yes"]
    # if save_pos_disable is not None:
    #     save_pos_disable = save_pos_disable in ["true", "1", "yes"]
    if skip is not None:
        skip = int(skip)
    if limit is not None:
        limit = int(limit)
    # if case_permute is not None:
    #     case_permute = case_permute in ["true", "1", "yes"]

    # Build the command list based on non-None values
    command = [prince_run_file]


    prince_wordlist = clean_path(prince_wordlist)
    output_file = clean_path(output_file)

    if prince_wordlist is not None:
        command.append(prince_wordlist)
    if keyspace:
        command.append("--keyspace")
    if pw_min is not None:
        command.append(f"--pw-min={pw_min}")
    if pw_max is not None:
        command.append(f"--pw-max={pw_max}")
    if elem_cnt_min is not None:
        command.append(f"--elem-cnt-min={elem_cnt_min}")
    if elem_cnt_max is not None:
        command.append(f"--elem-cnt-max={elem_cnt_max}")
    if wl_dist_len:
        command.append("--wl-dist-len")
    if wl_max is not None:
        command.append(f"--wl-max={wl_max}")
    if dupe_check_disable:
        command.append("--dupe-check-disable")
    if save_pos_disable:
        command.append("--save-pos-disable")
    if skip is not None:
        command.append(f"--skip={skip}")
    if limit is not None:
        command.append(f"--limit={limit}")
    if output_file is not None:
        command.append(f"--output-file={output_file}")
    if case_permute:
        command.append("--case-permute")
    return command


def genPrinceCommandHashcat(
    prince_run_file=None,
    prince_wordlist=None,
    keyspace=None,
    pw_min=None,
    pw_max=None,
    elem_cnt_min=None,
    elem_cnt_max=None,
    # wl_dist_len=None,
    wl_max=None,
    dupe_check_disable=None,
    save_pos_disable=None,
    skip=None,
    limit=None,
    case_permute=None
):

    # Convert strings to appropriate types
    # if keyspace is not None:
    #     keyspace = int(keyspace)
    if pw_min is not None:
        pw_min = int(pw_min)
    if pw_max is not None:
        pw_max = int(pw_max)
    if elem_cnt_min is not None:
        elem_cnt_min = int(elem_cnt_min)
    if elem_cnt_max is not None:
        elem_cnt_max = int(elem_cnt_max)
    # if wl_dist_len is not None:
    #     wl_dist_len = wl_dist_len in ["true", "1", "yes"]
    if wl_max is not None:
        wl_max = int(wl_max)
    # if dupe_check_disable is not None:
    #     dupe_check_disable = dupe_check_disable in ["true", "1", "yes"]
    # if save_pos_disable is not None:
    #     save_pos_disable = save_pos_disable in ["true", "1", "yes"]
    if skip is not None:
        skip = int(skip)
    if limit is not None:
        limit = int(limit)
    # if case_permute is not None:
    #     case_permute = case_permute in ["true", "1", "yes"]

    # Build the command list based on non-None values
    command = [prince_run_file]
    prince_wordlist = clean_path(prince_wordlist)

    if prince_wordlist is not None:
        command.append(prince_wordlist)
    if keyspace:
        command.append(f"--keyspace")
    if pw_min is not None:
        command.append(f"--pw-min={pw_min}")
    if pw_max is not None:
        command.append(f"--pw-max={pw_max}")
    if elem_cnt_min is not None:
        command.append(f"--elem-cnt-min={elem_cnt_min}")
    if elem_cnt_max is not None:
        command.append(f"--elem-cnt-max={elem_cnt_max}")
    # if wl_dist_len:
    #     command.append("--wl-dist-len")
    if wl_max is not None:
        command.append(f"--wl-max={wl_max}")
    if dupe_check_disable:
        command.append("--dupe-check-disable")
    if save_pos_disable:
        command.append("--save-pos-disable")
    if skip is not None:
        command.append(f"--skip={skip}")
    if limit is not None:
        command.append(f"--limit={limit}")
    if case_permute:
        command.append("--case-permute")
    return command
