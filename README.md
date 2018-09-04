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
  PATH                 Path to .msk file.

optional arguments:
  -h, --help           show this help message and exit
  --goal GOAL          Word count target.
  --start START_COUNT  Set the session start value.

$ ./session_wc.py --goal 750 ~/Documents/test.msk 
10/750 - Session; 133 start; 143 total 
```

Todo: 

* Method to reset the session and change goal without exiting the program.
* Use Manuskripts libraries and methods, rather than recoding the parsing of the save file.  In my defense I'm not sure if the calls in loadSave.py are stable or not and I only really had to read a tiny bit of the save file.  
* A curses (or something) progress bar like display
* Add interval as an option

Caveats:

* Works with the v1 single .msk file, not directory structure version or previous v0 save structure.
* It worked on my 0.7 installation/save files
* This readme contains just enough detail so if a future perspective employer looks at it, I'm not embarrassed, but only barely.  I don't suspect anyone besides myself will have much interest in this. 