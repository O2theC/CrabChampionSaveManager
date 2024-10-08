# CrabChampionSaveManager

sorry for the inactivity but i got intrested in other games along with life getting in the way, schools give way too much homework IMO, but i am still interested in Crab Champions along with this program, i want to work on it more but i have come to realize a few things    
1. The code is all in 1 file and is at around 6000 lines, while there is a lot of formating space, this is still a lot and it's getting harder to add new stuff  
2. I have learned more about making a program like this and would do things differently, i never thought it would be as feature rich as it is now and as such didn't plan the program well  
3. the TUI is ok but a GUI is better  

as such along with other reasons, i have decided on a few things   
i need to remake the entire thing - while i will likely be copying a lot of code, i will be remaking a lot of the logic and flow of logic, this includes making it into more than 1 big file   
while the TUI works, a GUI is so much better - this will allow more people to use it , not everyone likes a TUI nor can understand it as much as they can a GUI, i have also learned about PySimpleGUI and intend to use that to create a GUI for the program    

i have also noticed that the game is getting a biggish update soon and i am uncertain whether to wait till after, most likely since the program will not likely be done before then but we'll see   
i hope CCSM helps others with whatever they want to do on Crab Champions, whether that be content creation or build testing or something else    




a save manager for Crab Champions, made in Python 

currently going through refactor to make it easy to maintain and make it work with latest version of Crab Champions

made this for a group of friends to manage saves easier 
feel free to use it yourself

Main Credits:<br>
Pyinstaller - used to make .exe versions of the script so that it can be run without having to get python or uesave<br>
afkaf - made a sav converter in python, this reduces overhead and makes the program much faster when converting sav files, it also means the program won't make any temp json files like it did with uesave, he made it into pypi, you can find it here https://pypi.org/project/SavConverter/<br>
ChatGPT - used for some comments and code snippets, i am still learning about python after all<br>

# Install:  
download the program and then run it
### Windows: 
[Executable download (.exe)](https://github.com/O2theC/CrabChampionSaveManager/releases/latest/download/CrabChampionSaveManager.exe) - do this if you don't know what to do  
[Python script download (.py)](https://github.com/O2theC/CrabChampionSaveManager/releases/latest/download/CrabChampionSaveManager.py)  
### Linux
[Python script download (.py)](https://github.com/O2theC/CrabChampionSaveManager/releases/latest/download/CrabChampionSaveManager.py)  
# Use:
just run the file and it should start up
# Wiki
i am making a wiki for the program and parts of the game as it relates to CCSM  
List of maps with pictures : [Maps](https://github.com/O2theC/CrabChampionSaveManager/wiki/Maps)
<br>  
<br>  



# FAQ:<br>
Q: Can I help write and commit code?<br>

A: This is my first biggish project and as such I would rather write it myself, but that doesn't mean I won't "borrow" any code in an issue or pull request, feature requests, suggestions, and ideas are welcome  

Q: I have questions about the program, how can i contact you?

A: either submit an issue with your question or send me a msg to my discord( o2c )

Q: i have suggestions for the program

A: great, make an issue with your suggestion and why you think it would be useful or send my a msg to my discord( o2c ) and i will check it out

Q: i have a problem with the program

A: check the wiki, it may or may not have info about common issues, other wise make an issue or contact me on discord at o2c

Q: my antivirus flags this as malware / virus

A: this is not malware or a virus , check it on virustotal (it has been known to get hit by a few vendors but last i checked, it was at max 4 out of 70 vendors ), plus if you want then look through the source code / use the source code
<br>
<br>
<br>
Some other projects that are kind of similar to this one, in no particular order<br><br>
a web-based save converter to turn your .sav to JSON and back - https://afkaf.github.io/Crab-Champion-Save-Manager/ - https://github.com/afkaf/Crab-Champion-Save-Manager - credit to afkaf for making a python sav converter for CCSM<br>
item wiki for the game - https://crabchampions.info
