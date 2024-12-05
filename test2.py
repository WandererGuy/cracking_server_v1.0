from tqdm import tqdm


def potfile_to_wordlist():

    potfile = r'wordlist_samples\potfile_zing.txt'
    wordlist_file = r'wordlist_samples\tailieuvn_smallwordlist.txt'
    new_wordlist_file = r'wordlist_samples\zing_tailieuvn_smallwordlist.txt'

    wordlist = []
    with open (wordlist_file, 'r', encoding = 'utf-8') as f :
        lines = f.readlines()
        for line in tqdm(lines, total = len(lines)):
            line = line.strip('\n')
            if line != '':
                wordlist.append(line)
    with open (potfile, 'r', encoding = 'utf-8') as f :
        lines = f.readlines()
        for line in tqdm(lines, total = len(lines)):
            line = line.strip('\n').strip()
            if ":"  in line:
                hash, word = line.split(':', 1)
                wordlist.append(word)

    new_wordlist = set(wordlist)
    new_wordlist = sorted(new_wordlist, key = lambda x: (len(x), x))
    with open(new_wordlist_file, 'w', encoding = 'utf-8') as fout:
        for item in tqdm(new_wordlist, total = len(new_wordlist)):
            fout.write(item+'\n')

def collect_cracked_md5_hash():
    potfile_ls = ['wordlist_samples\potfile_tailieuvn.txt', 
                    'wordlist_samples\potfile_zing.txt'
                    ]
    all_cracked = {}
    collected_crack_path = 'wordlist_samples\potfile_tailieuvn_zing_upper.txt'
    for potfile_path in potfile_ls:
        with open (potfile_path, 'r', encoding = 'utf-8') as f :
            lines = f.readlines()
            for line in tqdm(lines, total = len(lines)):
                line = line.strip('\n')
                if ':' in line:
                    hash, word = line.split(':', 1)
                    if word not in all_cracked.keys(): 
                        all_cracked[word] = hash # avoid hash collision , same hash for two word 
    with open (collected_crack_path, 'w', encoding = 'utf-8') as fout:
        for key, value in tqdm(all_cracked.items(), total = len(all_cracked.items())):
            fout.write(f'{value.upper()}:{key}\n')

def create_duplicate_pcfg():
    # pcfg loves duplicate password, to emphasize on generate rule favors real password more, i duplicate interested 
    # password (collected from potfile)
    ori_wordlist_path = 'wordlist_samples\zing_tailieuvn_smallwordlist.txt'
    potfile_ls = ['wordlist_samples\potfile_tailieuvn.txt', 
                    'wordlist_samples\potfile_zing.txt'
                    ]
    pcfg_train_wordlist = 'wordlist_samples\pcfg_train_wordlist.txt'
    wordlist = []
    with open (ori_wordlist_path, 'r', encoding = 'utf-8') as f :
        lines = f.readlines()
        for line in tqdm(lines, total = len(lines)):
            line = line.strip('\n')
            if line != '':
                wordlist.append(line)

    for potfile_path in potfile_ls:
        with open (potfile_path, 'r', encoding = 'utf-8') as f :
            lines = f.readlines()
            for line in tqdm(lines, total = len(lines)):
                line = line.strip('\n').strip()
                if ":"  in line:
                    hash, word = line.split(':', 1)
                    wordlist.append(word)
    with open(pcfg_train_wordlist, 'w', encoding = 'utf-8') as fout:
        for item in tqdm(wordlist, total = len(wordlist)):
            fout.write(item+'\n')


def remaining_uncracked_md5_hash():
    pass

if __name__ == '__main__':
    create_duplicate_pcfg()
