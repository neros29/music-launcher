# Music Launcher
This is a music launcher built to be used on linux, with any 24 bit color suporting terrminals. It relys on a diffrent proejct i built in c++ however the code in this repo is all python. This project I built for myself since i alwasy have hated the way most local first music apps work.
# Featers
This music launcher has consists of mostly four components.
1. A backend that contorls mpv over linux ipc
2. A cusotom algorithem for searching through a music data base.
3. A script to creat the music data  base, when pointed at a folder containg mp3 files.
4. A custom query laungege and tui interface to serach and play music from your libbray. 
# Compiling
To uses this project you must first be on linux with a terrminal that accepts full color, you need to have terminfo, as well as utf8proc installed on your system, then you just run the make file. This will clone my repo for my tuilib that i built as the tui backend for this project. 
The make command should just be `make` as it's a very simple make file.
# Show case
![image](images/img1.png)
