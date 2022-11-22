## Overview

This command line tool scans audio files by **musical key** and **BPM** and tags them accordingly. The script was created to provide a semi-automated to automated solution for preparing tracks for digital DJ mixes.

The script will back up your files to a backup folder and output new tagged versions to an output folder. It will ask you whether to batch overwrite any existing tags in these files, or to proceed on a case by case basis.

The script will detect and handle MP3, FLAC, M4A and WAV files.

## Requirements

- [keyfinder](https://pypi.org/project/keyfinder/)
- [mutagen](https://pypi.org/project/mutagen/)
- [ffmpeg-python](https://pypi.org/project/ffmpeg-python/)
- [ffmpeg](https://pypi.org/project/ffmpeg/)

see *requirements.txt* for details

## Instructions

to run the tool, simply have the required packages installed and have the music files you want to tag located in the same directory as *tag_tracks.py*. Then run the script (**`python tag_tracks.py`**)

## Possible improvements

- tag WAV files (see issue https://github.com/quodlibet/mutagen/issues/545)
- analyze BPM for mp3 and flac files (currently there are issues with *aubio* extracting BPM from files that are not in .wav format such as mp3, flac, etc.) since they are missing a *RIFF header*... (see possibly related issue https://github.com/aubio/aubio/issues/111)
