mGBA 3DS Forwarder
===================

This is a (currently) uptodate fork of [TobiasBielefeld](https://github.com/TobiasBielefeld)'s fork of mGBA, which was originally made to generate 3DS mGBA Homescreen Forwarders for individual games when the project was built as a .cia.


The changes I've made to the Tobias's original fork are that I've updated the base mGBA to the current latest release (0.10.0 as of 21-10-22), and I've provided a python script to automate the process of building forwarders. The script will generate .cia Forwarder files which are essentially each a version of mGBA that, when opened from the Home Menu, automatically boot a ROM from a specified path on your 3DS's SD card. These paths must unfortunately be specified at the time the .cia is built with this script, so if you move the ROM file the forwarder will fail to boot and you'll have to make a new one. Because the script builds an mGBA cia, the version will always be that of the source code packaged with this script, which is current 0.10.0, even if you have a newer version installed on your 3DS. They will share the same settings/config files however.


Warning
--------

 All games will still use the same mGBA/ folder on your SD-card for the configuration file.

 Each .cia file generated with this script will have a random title ID. I cannot guarantee that the random title ID generation won't generate an ID that is already used on your 3DS, which could lead to problems. I am not responsible for any issues that occur as a result of using this script, please do so at your own risk.

Prerequisites
--------------

This script requires a modern versions of the following installed on your system and accessible via PATH:

  - Python (3.9+)
  - Docker (should be able to run `docker run` from the commandline)
  

Set-up
-------

First you'll need to clone this repo, navigate to a folder where you'd like to keep it and run: `git clone git@github.com:HeyItsJono/mgba-3DS-Forwarder.git`.

Alternatively, if you're uncomfortable with a commandline you can go to `Code -> Download ZIP` on this page, and extract the source code somewhere.

Next you'll need to create a directory where your forwarder .CIA files will be generated. I usually name this folder `cias`.

Then, within `cias`, create one subfolder for each forwarder you wish to generate. The generated .CIA will be the same name as the subfolder.

Then, within **each** subfolder you need to supply three files:

  - `icon.icn`: This will contain the icon and name for the game as it appears in System Settings and on the Home Screen
  - `banner.bnr`: This will contain the banner for the game, as it appears on the Top Screen when selected on the Home Screen
  - `path.txt`: This should be a plain text file containing the complete and direct path to the ROM file on your 3DS SD Card you want mGBA to load
  	+ For example, I store my roms in `/roms/**system**/**romfile**`, so an example of mine is: `/roms/gba/Pokemon Fire Red.gba`
  	+ These can be any rom file that mGBA supports (e.g. GB, GBC, GBA)
 
Please ensure there are **only** the above 3 files in each of the subfolders. Do not leave any stray extra files in there or the script will not work.

To generate the `icon.icn` and `banner.bnr` files I like to use [NSUI](https://3ds.eiphax.tech/nsui). You can make a New Project for each ROM and once you've put in a name and icon and banner (the latter of which you can get from [Libretro](https://github.com/libretro-thumbnails)), you can export `icon.icn` and `banner.bnr` via `Project -> Export (icon/banner) binary...`.

As an example, the folder structure should look something like this:

```
mGBA-3DS-Forwarder
|_____mGBA3DSForwarder.py
|_____mgba (contains the sourcecode to build mgba)
|_____cias
      |_____amazingmirror
            |_____icon.icn
            |_____banner.bnr
            |_____path.txt
      |_____firered
            |_____icon.icn
            |_____banner.bnr
            |_____path.txt
      |_____emerald
            |_____icon.icn
            |_____banner.bnr
            |_____path.txt
```


Instructions
-------------

Once set-up is complete as above, you can run the script in one of three ways. Either:

  - Drag the `cias` folder onto `mGBA3DSForwarder.py` (easiest)
  - Run `mGBA3DSForwarder.py` and when prompted, input the **complete** path to the `cias` folder
  - From the command line you `cd mGBA-3DS-Forwarder`, then you can run `python mGBA3DSForwarder.py complete-path-to-cias-folder`

Do not provide relative paths to either of the second two options. The script should then run and generate one `.cia` forwarder file for each subfolder under the `cias` folder.
These `.cia` files can be found in the `cias` folder once the script has finished. Be warned that the build process can take some time, particularly on your first run.
Once you have your `.cia` files, transfer them to your 3DS and install them with FBI.


Copyright
----------

mGBA is Copyright © 2013 – 2022 Jeffrey Pfau. It is distributed under the [Mozilla Public License version 2.0](https://www.mozilla.org/MPL/2.0/). A copy of the license is available in the distributed LICENSE file.
The code to generate a forwarder .cia originally came from Tobias Bielefeld so I also do not claim ownership of that, I have simply ported it to the latest mGBA build.
Many thanks to both Tobias and Jeffrey without whom this would not be possible.

mGBA contains the following third-party libraries:

- [inih](https://github.com/benhoyt/inih), which is copyright © 2009 – 2020 Ben Hoyt and used under a BSD 3-clause license.
- [blip-buf](https://code.google.com/archive/p/blip-buf), which is copyright © 2003 – 2009 Shay Green and used under a Lesser GNU Public License.
- [LZMA SDK](http://www.7-zip.org/sdk.html), which is public domain.
- [MurmurHash3](https://github.com/aappleby/smhasher) implementation by Austin Appleby, which is public domain.
- [getopt for MSVC](https://github.com/skandhurkat/Getopt-for-Visual-Studio/), which is public domain.
- [SQLite3](https://www.sqlite.org), which is public domain.
