# CrabChampionSaveManager
a save manager for Crab Champions, made in Python 

made this for a group of friends to manage saves easier 
feel free to use yourself, it is text based, just run the file in the correct location

put the script in C:\Users\\*USER*\AppData\Local\CrabChampions\Saved
or the equivalent folder if saves are stored else where 
this is made for windows and some parts of the script use python's os.system() method to do os cmds , this for editing save files, as such i am unsure if this works on linux, if it does yay, if it doesn't then well, oh well, if someone else wants to fork and make it work for linux go ahead, you can also put in a pull request to make it work on linux

while this does edit save files , the script offloads the task to uesave , found at this repo https://github.com/trumank/uesave-rs
it is made in rust and so if you want to edit save files then you will need to install rust and install uesave , make sure to add it to path as the script assumes it is

i did use ChatGPT for some code and to add comments to the code

i think i covered everything about this , put in an issue if there are any questions
