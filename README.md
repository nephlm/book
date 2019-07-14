# ms_session_wc
Keep track of the wordcount for the session while editing a manuskript document.


Interrogates the Manuskript save file for the purpose of setting a wordcount goal and updating progress whenever the file changes. 
https://github.com/olivierkes/manuskript

This is a feature I found incredible useful from scrivener when it worked on my linux installation.  This implementation is ugly, but it gets the job done. 

Goal and path to the save file are passed on the command line. A start wordcount can also be passed.  If missing the current wordcount it is used.  

```
$ ./session_wc.py -h
usage: session_wc.py [-h] [--goal GOAL] [--start START_COUNT] PATH

Session word count.

positional arguments:
  PATH                 Path to .msk file or root directory of the save.

optional arguments:
  -h, --help           show this help message and exit
  --goal GOAL          Word count target.
  --start START_COUNT  Set the session start value.

$ ./session_wc.py --goal 750 ~/Documents/test_file.msk 
10/750 - Session; 133 start; 143 total 
$ ./session_wc.py --goal 750 ~/Documents/test_dir/
11/750 - Session; 182 start; 193 total 
```

Todo: 

* Method to reset the session and change goal without exiting the program.
* Use Manuskripts libraries and methods, rather than recoding the parsing of the save file.  In my defense I'm not sure if the calls in loadSave.py are stable or not and I only really had to read a tiny bit of the save file.  
* A curses (or something) progress bar like display
* Add interval as an option
* I believe this handles the compile option correctly, but I only saw compile values of 0 and 2, which suggests there is a 1 and I don't know how to make that happen or what the semantics of that are.  Find that out. 
* There are some inefficiencies in walking up the tree to check the compile options.  They should probably be cleaned up.  

Caveats:

* Works with the v1 single .msk file or directory, not previous v0 save structure.
* It worked on my 0.7 installation/save files
* This readme contains just enough detail so if a future perspective employer looks at it, I'm not embarrassed, but only barely.  I don't suspect anyone besides myself will have much interest in this. 

Editing the README file is now procrastination from writing my novel.  The program as a whole wasn't, but editing the file with all the possible todos...