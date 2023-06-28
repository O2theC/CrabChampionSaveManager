# CrabChampionSaveManager
a save manager for Crab Champions, made in Python 

made this for a group of friends to manage saves easier 
feel free to use it yourself, it is text-based, just run the file ~~in the correct location~~

~~put the script in C:\\Users\\\*USER*\\AppData\Local\\CrabChampions\\Saved
or the equivalent folder if saves are stored elsewhere, easy way to get to it is by starting the Run program , use your search bar , then in the field doing %APPDATA%\\..\\Local\\CrabChampions\\Saved and then running that, you can do it in the location bar in file explorer and it should direct you to the correct folder, make sure though , this is only for the default location that the game is installed in~~

you should be able to run the script from anywhere and it should work, as long the game is installed in the default location, otherwise put it 1 folder away from the SaveSlot.sav file
example, save is at folderA/Folderb/CrabChampions/Saved/SaveGames/SaveSlot.sav, put the script in Saved folder

this is made for windows and some parts of the script use python's os.system() method to do os cmds , this for editing save files, as such I am unsure if this works on linux, if it does yay, if it doesn't then well, oh well, if someone else wants to fork and make it work for linux go ahead, you can also put in a pull request to make it work on linux

while this does edit save files, the script offloads the task to uesave, found at this repo https://github.com/trumank/uesave-rs
it is made in Rust and so if you want to edit save files then you will need to install Rust and install uesave, make sure to add it to path as the script assumes it is

I did use ChatGPT for some code and to add comments to the code

I think I covered everything about this, put in an issue if there are any questions

I used auto py to exe to turn the script to an exe, https://pypi.org/project/auto-py-to-exe/, nice and easy to use, I recommend it for small things like this, not sure if it would work for bigger or more complicated projects
