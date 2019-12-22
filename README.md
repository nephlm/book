# book

Maintain, monitor and modify a file structure and files based on the (manuskript)[https://github.com/olivierkes/manuskript] file structure.  This would be if settings were set not to save as a single .msk file or if that file were unzipped.

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

## config.yaml

The novel many have a `config.yaml` in the root of the novel.  Right now the only supported option in the file is:

* `tiddlywiki`: If this is set to a tiddlyspot or similar url that will serve a tiddlywiki file, then when session is running it will download and extract the tiddlers every 10 minutes.  The tiddlers are stored under in `world/tiddlers.json`

## Subcommands 

The main command is `book` and like with git there is a required subcommand.  Path is a required argument to all subcommands.  With the exception of some permutations of `new` this is always the folder containing the `MANUSKRIPT` file.

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

Folders and scenes must be created as file starting with a number.  This number may be an integer or decimal number.

```
$ book new ~/Documents/my_novel/outline/1-chapter/1.5-scene.md
```
Rename will rename all the folders and scenes with integer order numbers to keep everything orderly.  It will also use the title from the file metadata during the rename.  
```
$ book rename ~/Documetns/my_novel/outline/1-chapter/1.5-scene.md
```
You'll need to confirm the renames.

### Session

Keep track of the wordcount for the session while editing a novel.

Interrogates the novel files for the purpose of setting a wordcount goal and updating progress whenever the file changes. 

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

If you novel is in a git repo, then While session is running the novel will be committed and pushed to a git remote repo every 10 minutes. 

Github now has private repos so there is no excuse. 

### Stats

Some basic stats about scenes.  Generally prints out the titles of the scenes in order.  Also includes word counts and the order number within the folder it is in.

It also shows the total word count and max pk.  Now that the `new` command exists the max pk isn't that relevant anymore.  This whole command is nearly only useful as debugging.

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

Manuscript and scrivener export saves in `.mmd` format with hardcrlf, but that isn't as natural to edit as softcrlf with spaces between paragraphs.  These flags will flip between the two modes. 

### Compile

There is basic support for compiling into an ebook.  Right now this is a pretty basic feature.  

This requires pandoc and will export to an epub format 
```
$ book compile ~/Documents/mynovel/
```

Compile will write to `build/single_file.md` and `build/book.epub`.  `single_file.md` is a cleaned and concatanated version of the whole novel, while `book.epub` is the compiled epub.

Todo 
* Fill in frontmatter from config.yaml
* Custom css
* backmatter?
* Customize chapter headings.

## Outdated

The whole nature of this project has changes as I migrated off manuskipt to editing the `.md` files directly.  This is left over stuff that I need to look through, but it should be considered dated.

Todo: 

* Method to reset the session and change goal without exiting the program.
* A curses (or something) progress bar like display for session.
* Add interval as an option to session

Caveats:

* Works with the v1 single .msk file or directory, not previous v0 save structure.
* It worked on my 0.7 installation/save files
* This readme contains just enough detail so if a future perspective employer looks at it, I'm not embarrassed, but only barely.  I don't suspect anyone besides myself will have much interest in this. 

Editing the README file is now procrastination from writing my novel.  The program as a whole wasn't, but editing the file with all the possible todos...