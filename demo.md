for backend first then user 


# status API 

--status 
--status-json 
--status-timer 5 


# output recovery hash 
-o output.txt

# session , save and restore cracking seesssion 
press c button instead of q  -> to proper stop , suddenly stop will restore to nearest auto session restore point 
--session session_name
--session session_name --restore

# spefic to potfile path 
--potfile-path  

# -r rule file 


# run time 
     --runtime                  | Num  | Abort session after X seconds of runtime             | --runtime=10

# abort session 
press c button instead of q

# increment 
hashcat.exe --increment --increment-min=1 -d <include_gpu_numbers> -m 1000 -a 3 --session <name_your_session> <ntlm_hashes.txt> ?a?a?a?a?a?a?a -O

hashcat -a 3 -m 0 --session session2 --increment --increment-min=1 -o /home/manh264/Desktop/cracking_server/src/app/static/cracked_hash/gay.txt d1bba52026251f09fd62d8092aea077a ?a?a?a?a?a?a


hashcat --session session2 --restore-file-path ~/.local/share/hashcat/sessions


68bbcd498c20b85af566e2675701882a

copy ~/.local/share/hashcat/sessions/<session_name> -> src/app/session
del ~/.local/share/hashcat/hashcat.potfile

hashcat --session session2 --restore


d1bba52026251f09fd62d8092aea077a


policy (targuess )



dictionary attack for small wordlist 
apply rule file 


brute force 1-7 char
hashcat -a attack_mode -m hash_type --session session_name --increment --increment-min=1 -o output_file hash_file ?a?a?a?a?a?a

run through bigggest wordlist i have 
apply rule file 


bruteforce by digit up to 15 char (for phone and date of birth )

brute force mask (massive breach , little time )

pcfg dictionary 
apply rule file 

targuess mask brute force 
apply rule file 


brute force mask (massive breach , medium time )

prince 

brute force mask (massive breach , big time )



must run 

hashcat -a attack_mode -m hash_type --session session_name --increment --increment-min=1 -o output_file hash_file ?a?a?a?a?a?a


hashcat -a attack_mode -m hash_type --session session_name --increment --increment-min=1 -o output_file hash_file ?a?a?a?a?a?a
