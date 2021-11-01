## overview

This script allows you to quickly scan and tag your audio files by musical key. The script will back up your files and output new tagged versions to an output folder. You can choose to batch overwrite any existing tags in these files, or proceed on a case by case basis. The script was created to provide an automated and software-free solution for preparing tracks for digital DJ mixes.

## requirements

- [keyfinder](https://pypi.org/project/keyfinder/)
- [mutagen](https://pypi.org/project/mutagen/)
- [ffmpeg-python](https://pypi.org/project/ffmpeg-python/)
- [ffmpeg](https://pypi.org/project/ffmpeg/)

see `requirements.txt` for details

## instructions

to run the tool, simply have the required packages installed and have the music files you want to tag located in the same directory as `tag_tracks.py`. Then simply run the script (**`python tag_tracks.py`**)

## possible improvements

- tag WAV files (see issue https://github.com/quodlibet/mutagen/issues/545)
- analyze BPM for mp3 and flac files (currently there are issues with `aubio` extracting BPM from files that are not in .wav format such as mp3, flac, etc.) since they are missing a `RIFF header`... (see possibly related issue https://github.com/aubio/aubio/issues/111)