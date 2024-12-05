

I. for kali (but i dont use kali anymore)


Intsall VScode 
https://phoenixnap.com/kb/install-deb-files-ubuntu
sudo dpkg -i <package path>

Install venv 
https://gist.github.com/Geoyi/d9fab4f609e9f75941946be45000632b

sudo apt update -y
sudo apt install python3 -y 
cd /home/manh264/Desktop/kali_api
python3 -m venv env
source env/bin/activate 
pip install fastapi uvicorn pydantic python-multipart tqdm


II. for window :
install conda 
conda create ... python==3.10
conda activate ...
pip install fastapi uvicorn pydantic python-multipart tqdm


III. For window
how to build from source 
notice that: Cygwin maps Windows drives under /cygdrive/, thats how u can access window file in cygwin

first install cygwin 
can download like online vid 
https://www.youtube.com/watch?v=J3XQbrJ2GeU


or like jtr set up is also ok 
https://github.com/openwall/john/blob/bleeding-jumbo/doc/INSTALL


after that :
tackle issue of ssl
For ssl 
In folder download setup-x86_64.exe for cygwin , open terminal  
setup-x86_64.exe -q -P openssl-devel
setup-x86_64.exe -q -P openssl
setup-x86_64.exe -q -P libssl-dev -P libssl-devel


HEADS UP NOTICE: to build/compile jtr + hydra from source with cygwin :
1. in cygwin terminal do : ./configure 
Inside the folder, do a ./configure This will check all your environment variables, paths, etc and create a 'make' file. 
2. Then in cygwin terminal do : make
 That should compile a binary. 
3. Then in cygwin terminal do : make install
 make install Will essentially copy the main program elements into the proper places to run the app.. However, this does not take into account dependencies... (Which is what apt-get, dpkg, emerge take care of...)
4. then the exe file will appear in folder, which is done, now u can call hydra inside hydra folder 


-------- jtr --------
https://github.com/openwall/john/blob/bleeding-jumbo/doc/INSTALL


will have to copy all cygwin dll missing into same folder run hashcat or jtr , dll will be noticed by window as missing (dll from folder install cygwin)


-------- hydra --------
https://github.com/vanhauser-thc/thc-hydra
HOW TO COMPILE
--------------
To configure, compile and install hydra, just type: (same as jtr)

```
./configure
make
make install
```


-------- hashcat --------
https://www.msys2.org/docs/updating/
https://github.com/hashcat/hashcat/blob/master/BUILD_MSYS2.md



