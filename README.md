# ms_session_wc

TODO: change the project name given the change in scope.

Maintain, monitor and modify a file structure and files based on the (manuskript)[https://github.com/olivierkes/manuskript] file structure.  This would be setting were set to not to save as a single .msk file or if that file were unzipped.

The resulting structure is only close to the manuscript format, no attempt will be made to keep them cross compatible.  It will work with a file structure created my manuskript, manuskript will probably not work with a file structure created by this script.

## Deviations

* There is an optional `novel.md` in the `outline` directory
* The following files and directory are not created at present.
  * `characters/`
  * `infos.txt`
  * `labels.txt`
  * `plots.xml`
  * `revisions.xml`
  * `settings.txt`
  * `status.txt`
  * `summary.txt`
  * `world.opml`

I generally use (tiddlywiki)[https://tiddlywiki.com] for my world bible and the rest of these files are two structured for my needs. 

The only think I'll truly miss is revisions.  I use git and a private repo for those.  Eventually I'll add a fs monitor and automatic commits, but not there yet. 

## Subcommands 

The main command is `book` and like with git there is a required subcommand.  Path is a required argument to all subcommands.  With the exception of some permutations of `new` this is alwasy the folder containing the `MANUSKRIPT` file.

### New

Create a new novel, folder or scene.


A new novel is created if there is no parent directory containing `MANUSKRIPT`.
```
$ book new ~/Documents/my_novel
new novel: /home/nephlm/Documents/my_novel
```
A folder is created if the path does not end in `.md` (or `.txt`).

```
$ book new ~/Documents/my_novel/outline/1-chapter1
new folder /home/nephlm/Documents/my_novel/outline/1-chapter in novel /home/nephlm/Documents/my_novel
```
Otherwise a scene is created.
```
$ book new ~/Documents/my_novel/outline/1-chapter/1-scene.md
new scene /home/nephlm/Documents/my_novel/outline/1-chapter/1-scene.md in novel /home/nephlm/Documents/my_novel
```

The preceding numbers for chapters and scenes are not optional, it is how ordering is tracked.

### Rename

Folders and scenes can be created with float order numbers.

```
$ book new ~/Documetns/my_novel/outline/1-chapter/1.5-scene.md
```
Rename will rename all the folders and scenes to integer order numbers to keep everything orderly.
```
$ book rename ~/Documetns/my_novel/outline/1-chapter/1.5-scene.md
```
You'll need to confirm the renames.

### Session

Keep track of the wordcount for the session while editing a manuskript document.


Interrogates the Manuskript save file for the purpose of setting a wordcount goal and updating progress whenever the file changes. 

This is a feature I found incredible useful from scrivener when it worked on my linux installation. 

Goal and path to the save file are passed on the command line. A start wordcount can also be passed.  If missing the current wordcount it is used.  

```
$ book session -h
usage: book session [-h] [--goal GOAL] [--start START_COUNT]

optional arguments:
  -h, --help           show this help message and exit
  --goal GOAL          Word count target.
  --start START_COUNT  Set the session start value.


$ book session --goal 750 ~/Documents/my_novel
11/750 - Session; 182 start; 193 total 
```

### Stats

Some basic stats about scenes.  Generally prints out the titles of the scenes in order.  Also includes word counts and the order number within the folder it is in.

It also shows the total word count and max pk.  Now that the `new` command the max pk isn't that relevant anymore.  This whole command is nearly only useful as debugging.

```
$ book stats ~/Documents/my_novel
01,   514, Waking up
02,    96, Back to work.
count = 610
max pk = 4
```

### Transform

Package up some transformations.  Doesn't do anything without additional flags.

* `--softcrlf` - Adds line feed between paragraphs.
* `--hardcrlf` - Removes the extra line feeds between paragraphs.

Transforms are applied to all scenes.

```
$ book transform --softcrlf
```

Manuscript saves in `.mmd` format with hardcrlf, but that isn't as natural to edit as softcrlf with spaces between paragraphs.  These flags will flip between the two modes. 

## Outdated

The whole nature of this project has changes as I migrated off manuskipt to editing the `.md` files directly.  This is left over stuff that I need to look through, but it should be considered dated.

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