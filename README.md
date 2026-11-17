## Overview

This command line tool scans audio files by **musical key** and **BPM** and tags them accordingly. The script was created to provide a semi-automated to automated solution for preparing tracks for digital DJ mixes.

The script will back up your files to a backup folder and move the tagged versions to an output folder. It will ask you whether to batch overwrite any existing tags in these files, or to proceed on a case by case basis.

The script will detect and handle MP3, FLAC, M4A and WAV files.

## Requirements

- [keyfinder](https://pypi.org/project/keyfinder/)
- [mutagen](https://pypi.org/project/mutagen/)
- [ffmpeg-python](https://pypi.org/project/ffmpeg-python/)
- the `ffmpeg` and `aubio` command line tools on your PATH (on Ubuntu: `apt install ffmpeg aubio-tools`)

see *requirements.txt* for details

## Instructions

to run the tool, simply have the required packages installed and have the music files you want to tag located in the same directory as *tag_tracks.py*. Then run the script (**`python tag_tracks.py`**)

For unattended runs (e.g. from a download pipeline), **`python tag_tracks.py --defaults`** answers every question with its default: only files missing a key or BPM get analyzed, and existing values are left alone.

## Crash handling

Some mp3s contain a corrupt frame that makes keyfinder's built-in decoder abort, which used to kill the whole run with `Segmentation fault (core dumped)` (see [keyfinder-py#2](https://github.com/EvanPurkhiser/keyfinder-py/issues/2)). The script now decodes each track once with the ffmpeg CLI, which skips bad frames, and runs keyfinder and aubio on that temporary WAV. keyfinder also runs in a child process, so any remaining crash only fails that one file and is listed in the error summary at the end.

## Possible improvements

I wouldn't mind help with the following:

- tagging WAV files directly (see issue https://github.com/quodlibet/mutagen/issues/545)
