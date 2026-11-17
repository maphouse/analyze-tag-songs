from glob import glob
import argparse
import os
import shutil
import sys
import tempfile
import ffmpeg
import subprocess
from math import trunc
from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.id3 import TKEY
from mutagen.id3 import TKE
from mutagen.id3 import TXXX
from mutagen.id3 import TBPM
from mutagen.id3 import COMM
from mutagen.flac import FLAC

#colors for command line tool readability

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    UNDERLINE = '\033[4m'

#'playlist key':[['theoretical key options'...],'camelot key',base frequency]
#frequency of notes based on https://pages.mtu.edu/~suits/notefreqs.html

key_dict = {
    '1':[['C'],'8B',[16.35,32.70,65.41,130.81,261.63,523.25,1046.50,2093.00,4186.01]],
    '2':[['Am'],'8A',[27.50,55.00,110.00,220.00,440.00,880.00,1760.00,3520.00,7040.00]],
    '3':[['Em'],'9A',[20.60,41.20,82.41,164.81,329.63,659.25,1318.51,2637.02,5274.04]],
    '4':[['G'],'9B',[24.50,49.00,98.00,196.00,392.00,783.99,1567.98,3135.96,6271.93]],
    '5':[['D'],'10B',[18.35,36.71,73.42,146.83,293.66,587.33,1174.66,2349.32,4698.63]],
    '6':[['Bm'],'10A',[30.87,61.74,123.47,246.94,493.88,987.77,1975.53,3951.07,7902.13]],
    '7':[['F#m','Gbm'],'11A',[23.12,46.25,92.50,185.00,369.99,739.99,1479.98,2959.96,5919.91]],
    '8':[['A'],'11B',[27.50,55.00,110.00,220.00,440.00,880.00,1760.00,3520.00,7040.00]],
    '9':[['E'],'12B',[20.60,41.20,82.41,164.81,329.63,659.25,1318.51,2637.02,5274.04]],
    '10':[['Dbm'],'12A',[17.32,34.65,69.30,138.59,277.18,554.37,1108.73,2217.46,4434.92]],
    '11':[['Abm'],'1A',[25.96,51.91,103.83,207.65,415.30,830.61,1661.22,3322.44,6644.88]],
    '12':[['B'],'1B',[30.87,61.74,123.47,246.94,493.88,987.77,1975.53,3951.07,7902.13]],
    '13':[['F#','Gb'],'2B',[23.12,46.25,92.50,185.00,369.99,739.99,1479.98,2959.96,5919.91]],
    '14':[['Ebm'],'2A',[19.45,38.89,77.78,155.56,311.13,622.25,1244.51,2489.02,4978.03]],
    '15':[['Bbm'],'3A',[29.14,58.27,116.54,233.08,466.16,932.33,1864.66,3729.31,7458.62]],
    '16':[['Db','C#'],'3B',[17.32,34.65,69.30,138.59,277.18,554.37,1108.73,2217.46,4434.92]],
    '17':[['Ab','G#'],'4B',[25.96,51.91,103.83,207.65,415.30,830.61,1661.22,3322.44,6644.88]],
    '18':[['Fm'],'4A',[21.83,43.65,87.31,174.61,349.23,698.46,1396.91,2793.83,5587.65]],
    '19':[['Cm'],'5A',[16.35,32.70,65.41,130.81,261.63,523.25,1046.50,2093.00,4186.01]],
    '20':[['Eb','D#'],'5B',[19.45,38.89,77.78,155.56,311.13,622.25,1244.51,2489.02,4978.03]],
    '21':[['Bb','A#'],'6B',[29.14,58.27,116.54,233.08,466.16,932.33,1864.66,3729.31,7458.62]],
    '22':[['Gm'],'6A',[24.50,49.00,98.00,196.00,392.00,783.99,1567.98,3135.96,6271.93]],
    '23':[['Dm'],'7A',[18.35,36.71,73.42,146.83,293.66,587.33,1174.66,2349.32,4698.63]],
    '24':[['F'],'7B',[21.83,43.65,87.31,174.61,349.23,698.46,1396.91,2793.83,5587.65]]
}

bpm_list = [115,122,127,135]

freq_list = []

def compile_freqs_to_list():
    for x in key_dict.items():
        freqs = [y for y in x[-1][-1]]
        freq_list.extend(freqs)
    #freq_list.sort()
    #print(freq_list)

def format_question(s):
    return f"{bcolors.WARNING}"+str(s)+f"{bcolors.ENDC}"
    
def format_val(s):
    return f"{bcolors.OKBLUE}"+str(s)+f"{bcolors.ENDC}"
    
def format_conf(s):
    return f"{bcolors.OKGREEN}"+str(s)+f"{bcolors.ENDC}"
    
def format_warning(s):
    return f"{bcolors.OKCYAN}"+str(s)+f"{bcolors.ENDC}"
    
def format_underline(s):
    return f"{bcolors.UNDERLINE}"+str(s)+f"{bcolors.ENDC}"
    
def format_error(s):
    return f"{bcolors.FAIL}"+str(s)+f"{bcolors.ENDC}"


def backup(file):
    
    backupdir = 'backup'
    if not os.path.isdir(backupdir):
        print('Creating backup folder ./'+backupdir)
        os.mkdir(backupdir)
    else:
        pass
        
    shutil.copy(file, './'+backupdir)
    print(format_conf('Created backup for ')+format_val(file)+format_conf(' in ./')+format_conf(backupdir))

#function for converting wav and m4a and then deleting original
def convert_media(f):
    if f.split('.')[-1] == 'wav':
        acodec = 'flac'
        ext = '.flac'
        params = [acodec]
    elif f.split('.')[-1] == 'm4a':
        acodec = 'libmp3lame'
        ext = '.mp3'
        ab = '320k'
        params = [acodec, ab]
        
    try:
        print(format_conf('Converting ')+format_val(f)+format_conf(' to ')+format_val(ext)+format_conf(' for compatibility'))
        i = ffmpeg.input(f)
        filename = '.'.join(f.split('.')[:-1])
        if f.split('.')[-1] == 'wav':
            output = ffmpeg.output(i,filename+ext,acodec=acodec)
        elif f.split('.')[-1] == 'm4a':
            output = ffmpeg.output(i,filename+ext,acodec=acodec, ab=ab)
        output.run()
    except Exception as e:
        print(format_error(e))
        print('ffmpeg encountered an error. Skipping conversion for '+f)
        return
    else:
        print(f+' converted successfully, deleting original.')
        os.remove(f)

#decode a track once to a temporary wav, shared by key and bpm analysis.
#the ffmpeg CLI skips corrupt mp3 frames ("Header missing"), whereas the decoder
#inside keyfinder aborts on them and takes the whole python process down with a
#'Segmentation fault (core dumped)'. analyzing the clean wav avoids that.
wav_cache = {}

def get_wav(f):
    if f in wav_cache:
        return wav_cache[f]
    fd, wav = tempfile.mkstemp(suffix='.wav')
    os.close(fd)
    print(format_conf('Decoding ')+format_val(f)+format_conf(' to a temporary .wav for analysis'))
    result = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', f,
                             '-vn', '-c:a', 'pcm_s16le', wav], capture_output=True, text=True)
    if result.returncode != 0 or os.path.getsize(wav) == 0:
        os.remove(wav)
        raise RuntimeError('ffmpeg could not decode '+f+': '+result.stderr.strip()[-300:])
    wav_cache[f] = wav
    return wav

def clear_wav(f):
    wav = wav_cache.pop(f, None)
    if wav and os.path.exists(wav):
        os.remove(wav)
        
#function searches all tags in file that could already contain a key
def find_existing_keytags(f: 'mutagen.ID3/FLAC'):
    #print("SOLVE THIS f ",f)
    #if f[-4:] == 'flac':
    #    tags_obj = FLAC(f)
    #    possible_keytags = ['key','initialkey']
    #elif f[-3:] == 'mp3':
    #    tags_obj = ID3(f)
    #    possible_keytags = ['TKEY','TKE','TXXX:initialkey','TXXX:KEY']
    #print('f ',f)
    if isinstance(f, FLAC):
        possible_keytags = ['key','initialkey']
    elif isinstance(f, ID3):
        possible_keytags = ['TKEY','TKE','TXXX:initialkey','TXXX:KEY','TXXX:key']
        
    while True:
        for i,keytag in enumerate(possible_keytags):
            try:
                key = f[keytag][0]
                for val in key_dict.values():
                    if key in val[0]:
                        print('Found valid key '+key+' in tag \''+keytag+'\'')
                        return key
                    else:
                        pass
            except Exception as e:
                if i != len(possible_keytags):
                    pass
                else:
                    break
        return False

#returns the key as a string, or an Exception if detection failed.
#keyfinder runs in a child process so that a crash in its C++ code only fails
#this one file instead of killing the whole tagging run.
def keyfinder_scan(f):
    print('Running keyfinder on '+f)
    try:
        wav = get_wav(f)
        result = subprocess.run([sys.executable, '-c',
                                 'import sys, keyfinder; print(keyfinder.key(sys.argv[1]).standard())', wav],
                                capture_output=True, text=True, timeout=900)
    except Exception as e:
        return e
    key = result.stdout.strip()
    if result.returncode != 0 or not any(key in v[0] for v in key_dict.values()):
        return RuntimeError('keyfinder failed on '+f+' (exit code '+str(result.returncode)+'): '+result.stderr.strip()[-300:])
    print('Detected key '+key)
    return key

def return_bpm(f: 'mutagen') -> int:
    #raises if the file has no usable bpm; a bpm of 0 is a placeholder and counts as missing
    if isinstance(f,ID3):
        bpm = int(float(f['TBPM'][-1]))
    elif isinstance(f,FLAC):
        bpm = int(float(f['bpm'][-1]))
    if bpm <= 0:
        raise ValueError('placeholder bpm '+str(bpm))
    return bpm

#do not use outside this script since function depends on other funtions here if f is not wav
#this function converts to wav (if not wav) and analyzes for bpm and returns a bpm int, it also deletes the temporary wav that was created if it had to perform conversion
def analyze_bpm(f):
    try:
        wav = get_wav(f)
        #aubio cannot read mp3/flac directly, so it gets the decoded wav
        result = subprocess.run(['aubio', 'tempo', wav], capture_output=True, text=True)
        bpm = float(result.stdout.split()[0])
        print("BPM detected: ",bpm)
        bpm = str(trunc(bpm))
    except Exception as e:
        print(format_error(e))
        print('bpm analysis encountered an error. Skipping analysis for '+f)
        error_dict[f] = e
        return False
    return bpm
    
def return_playlistkey(k):
    for playlistkey, keys in key_dict.items():
        if k in keys[0]:
            return playlistkey
        else:
            pass
        
def return_camelotkey(k):
    for playlistkey, keys in key_dict.items():
        if k in keys[0]:
            return keys[1]
        else:
            pass

def return_freq(k):
    #print('k ',k)
    for playlistkey, keys in key_dict.items():
        if k in keys[0]:
            #return 4th octave (C4)
            #print('k ',k)
            #print('k -1 4',keys[-1][4])
            return keys[-1][4]
        else:
            pass

#based on equation found here https://forum.ableton.com/viewtopic.php?t=179711#p1401670
def calc_new_freq(original_bpm, original_freq, desired_bpm):
    #print('original_bpm ',original_bpm)
    #print('original_bpm ',type(original_bpm))
    #print('original_freq ',original_freq)
    #print('original_freq ',original_freq)
    #print('desired_bpm ',desired_bpm)
    #print('desired_bpm ',desired_bpm)
    new_freq = desired_bpm/original_bpm*original_freq
    #for x in key_dict.items():
        #for 
    return new_freq
    
def find_nearest_number(n, num_list = freq_list):
    #function relies on existence of global var list freq_list
    abs_differences = [abs(x - n) for x in num_list]
    #print(abs_differences)
    #print(min(abs_differences))
    min_diff = min(abs_differences)
    index_min = abs_differences.index(min_diff)
    #index_min_diff = min(abs_differences, key = lambda i: abs_differences[int(i)-5])
    print('nearest freq ',num_list[index_min])
    return num_list[index_min]

# conventions are based on https://exiftool.org/TagNames/ID3.html but many applications use TXXX:[descriptor] as well
def write_key(tags,k):
    if isinstance(tags, FLAC):
        tags["key"] = k
        tags["initialkey"] = k
        return tags
    elif isinstance(tags, ID3):
        id3 = tags
        id3.add(TKEY(encoding=3, text=k))
        id3.add(TKE(encoding=3, text=k))
        id3.add(TXXX(encoding=3, text=k, desc='initialkey'))
        id3.add(TXXX(encoding=3, text=k, desc='key'))
        #remove duplicate upper-case variants, but only when they hold the same key;
        #a differing value is someone's data and is left alone.
        tags_to_remove = ['TXXX:INITIALKEY','TXXX:KEY']
        for t in tags_to_remove:
            if t in id3 and str(id3[t].text[0]) == k:
                id3.pop(t)
        return id3
    '''
    elif f[-3:] == 'wav':
        id3 = WAVE(f)
        id3.add(TKEY(encoding=3, text=k))
    '''

#write any tag (t) to key (k) of file tag object (f)
def write_alt_key(f,k,t):
    if isinstance(f,ID3):
        f.add(TXXX(encoding=3, text=k, desc=t))
        return f
    elif isinstance(f,FLAC):
        f[t] = k
        return f

def write_bpm(f,k,t):
    if isinstance(f,ID3):
        #print('tagging mp3')
        f.add(TBPM(encoding=3, text=k))
        if 'TXXX:BPM' in f and str(f['TXXX:BPM'].text[0]) == k:
            f.pop('TXXX:BPM')
        return f
    #elif f is flac tag object
    elif isinstance(f,FLAC):
        f[t] = k
        return f

def write_repitched_camelot_key(f,k,t):
    if isinstance(f,ID3):
        #print('tagging mp3')
        f.add(TBPM(encoding=3, text=k))
        tags_to_remove = ['TXXX:BPM']
        for x in tags_to_remove:
            try:
                f.pop(x)
            except:
                continue
        return f
    #elif f is flac tag object
    elif isinstance(f,FLAC):
        #print('tagging flac')
        #print(f, ' ',k, ' ',t)
        f[t] = k
        return f
#-----

parser = argparse.ArgumentParser(description='Tag the audio files in the current directory by key and BPM.')
parser.add_argument('--defaults', action='store_true',
                    help='answer every question with its default (only fills in missing key/BPM tags); for unattended runs')
args = parser.parse_args()

#in --defaults mode every prompt gets the empty answer, i.e. its default
def ask(prompt):
    if args.defaults:
        print(prompt+' [default]')
        return ''
    return input(prompt)

#setup interview

while True:
    print(format_question('How do you wish to tag your files by ')+format_underline('musical key')+format_question('?\n'))
    keyscan_option = ask(format_question('[a] Scan all and overwrite existing key tags\n[b] Scan all and manually approve each overwrite\n[c] Only scan and tag files with missing key tags (default)\n[d] Skip\n'))
    if keyscan_option in ['a','b','c','d','']:
        break
while True:
    tag_camelot = ask(format_question('Apply/Overwrite ')+format_underline('Camelot tags')+format_question(' to files? ([y]/[n])\n'))
    if tag_camelot in ['y','','n']:
        break
while True:
    tag_playlist = ask(format_question('Apply/Overwrite ')+format_underline('Playlist tags')+format_question(' to files? (these are custom-defined codes that - when used to order songs in ascending or descending order - minimize tonal dissonance between songs during playback) ([y]/[n])\n'))
    if tag_playlist in ['y','','n']:
        break
while True:
    analyze_bpm_option = ask(format_question('[a] Analyze and overwrite ')+format_underline('BPM')+format_question('? ([y]/[n])\n[b] Analyze and write only missing ')+format_underline('BPM')+format_question(' values? (default)\n[c] Skip.\n'))
    if analyze_bpm_option in ['a','','c','b']:
        break
while True:
    repitch_keys = ask(format_question('Calculate and write/overwrite ')+format_underline('camelot key tags')+format_question(' for repitched track at following BPMs ')+format_val(bpm_list)+format_question('? ([y]/[n])\n'))
    if repitch_keys in ['y','','n']:
        break
'''
while True:
    rename_files = ask(format_question('Rename files according to the following format? ')+format_underline('%camelotkey%_%bpm%_%artist%_%title%'))
    if rename_files in ['y','','n']:
        break
'''

backed_up_list = []

wav_list = glob('*.wav')
if len(wav_list) > 0:
    while True:
        wav_conv_choice = ask(format_val(len(wav_list))+format_question(' .wav files require conversion to be tagged. Unconverted files will be ignored. Convert to .flac? (y/n)'))
        if wav_conv_choice in ['y','n','']:
            break

    if wav_conv_choice == 'y' or not wav_conv_choice:
        #backup(['.wav'])
        for file in wav_list:
            backup(file)
            backed_up_list.append('.'.join(file.split('.')[:-1]))
            convert_media(file)
        else:
            print('done wav conversions')
    else:
        pass
else:
    print("No .wav files found for conversion.")


m4a_list = glob('*.m4a')
if len(m4a_list) > 0:
    
    while True:
        m4a_conv_choice = ask(format_val(len(m4a_list))+format_question(' .m4a files require conversion to be tagged. Unconverted files will be ignored. Convert to mp3? (y/n)'))
        if m4a_conv_choice in ['y','n','']:
            break
    
    if m4a_conv_choice == 'y' or not m4a_conv_choice:
        #backup(['.wav'])
        for file in m4a_list:
            backup(file)
            backed_up_list.append('.'.join(file.split('.')[:-1]))
            convert_media(file)
        else:
            print('done m4a conversions')
    else:
        pass
else:
    print("No .m4a files found for conversion.")


#set up output directory

destdir = 'tagging_output'
if not os.path.isdir(destdir):
    os.mkdir(destdir)
else:
    pass

track_list = glob('*.mp3') + glob('*.flac')
tagged_count = 0
error_dict = {}

for file in track_list:
    
    print('')
    #drop the previous file's temporary wav (the loop has several early 'continue's)
    for leftover in list(wav_cache):
        clear_wav(leftover)
    
    #catch any missing metadata headers
    if file[-4:] == 'flac':
        tags_obj = FLAC(file)
        tags_obj_compare = FLAC(file)
    elif file[-3:] == 'mp3':
        try:
            tags_obj = ID3(file)
            tags_obj_compare = ID3(file)
        except ID3NoHeaderError:
            tags_obj = ID3()
            tags_obj.filename = file
            tags_obj_compare = ID3()
        except Exception as e:
            print(format_error(e))
            error_dict[file] = e
            continue
    
    #make sure to not back up a file that has already been backed up during conversion
    if '.'.join(file.split('.')[:-1]) not in backed_up_list and ((keyscan_option != 'd') or (tag_camelot != 'n') or (tag_playlist != 'n') or (analyze_bpm_option != 'c')):
        backup(file)

    if keyscan_option == 'a':
        
        tkey = keyfinder_scan(file)
        #keyfinder currently does not return a python exception if a 'Segmentation fault (core dump)' is encountered, which can happen with some audio files. The following error handling is still implemented for when this can be handled by python
        if isinstance(tkey, Exception):
            print(format_error(tkey))
            error_dict[file] = tkey
            continue
        else:
            print('Writing detected key tag '+tkey+' for ' + file)
            #file here
            tags_obj = write_key(tags_obj,tkey)
        
    elif keyscan_option == 'b':
        
        #file here
        tkey = find_existing_keytags(tags_obj)
        
        #tkey = id3['TKEY'][0]
        if tkey != False:
            keyscan_run = ask(format_val(file) + format_question(' already contains key tag ') + format_val(tkey) + format_question(', do you want to run keyfinder anyway? ([y]/[n])\n'))
            if keyscan_run == 'y' or not keyscan_run:
                key = keyfinder_scan(file)
                if isinstance(key, Exception):
                    print(format_error(key))
                    error_dict[file] = key
                    continue
                elif tkey != key:
                    while True:
                        key_overwrite = ask(format_val(file) + format_question(' already contains key tag ') + format_val(tkey) + format_question(' but keyfinder detected ') + format_val(key) + format_question('. Overwrite? ([y]/[n])'))
                        if key_overwrite in ['y','n','']:
                            break
                    if key_overwrite == 'y' or not key_overwrite:
                        print(format_conf('Overwriting key tags for ') + format_val(file))
                        #file here
                        tags_obj = write_key(tags_obj,key)
                        #id3.add(COMM(encoding=3, text='key tag '+tkey+' overwritten using libKeyFinder to '+key.standard()))
                    else:
                        print('No changes were made to key tag')
                        #distribute detected key tag anyway to other key tags (to account for inconsistent reading of ID3 tags in media players)
                        #file here
                        tags_obj = write_key(tags_obj,tkey)
                else:
                    print('keyfinder detected same key.')
                    print(format_conf('Overwriting key tags for ') + format_val(file))
                    #file here
                    tags_obj = write_key(tags_obj,key)
            else:
                print('No changes were made to key tag')
                #distribute detected key tag anyway to other key tags (to account for inconsistent reading of ID3 tags in media players)
                #file here
                tags_obj = write_key(tags_obj,tkey)
        elif tkey == False:
            print('Did not detect a key tag for '+file)
            key = keyfinder_scan(file)
            if isinstance(key, Exception):
                print(format_error(key))
                error_dict[file] = key
                continue
            else:
                print(format_conf('Writing key tag ')+format_val(key)+format_conf(' to ') + format_val(file))
                #file here
                tags_obj = write_key(tags_obj,key)
                tkey = key
            
    elif keyscan_option == 'c' or not keyscan_option:
        tkey = find_existing_keytags(tags_obj)
        if tkey != False:
            print(file + ' key already tagged with '+tkey+'.')
            #distribute detected key tag anyway to other key tags (to account for inconsistent reading of ID3 tags in media players)
            tags_obj = write_key(tags_obj,tkey)
        elif tkey == False:
            print('Did not detect a key tag for '+file)
            key = keyfinder_scan(file)
            if isinstance(key, Exception):
                print(format_error(key))
                error_dict[file] = key
                continue
            else:
                print(format_conf('Writing key tag ')+format_val(key)+format_conf(' to ') + format_val(file))
                tags_obj = write_key(tags_obj,key)
                tkey = key
            
            #id3.add(COMM(encoding=3, text='key tag '+key.standard()+' written using libKeyFinder.'))     
    #elif keyscan_option == 'd':
    #    print('No keys were scanned for '+file)
    elif keyscan_option == 'd':
        tkey = find_existing_keytags(tags_obj)
        pass
    
    if tag_camelot == 'y' or not tag_camelot:
        try:
            #print('tkey ', tkey)
            ckey = return_camelotkey(tkey)
        #exception will only occur if [d] was selected in melodic key question
        except Exception as e:
            tkey = find_existing_keytags(tags_obj)
            if tkey != False:
                ckey = return_camelotkey(tkey)
            elif tkey == False:
                print('Camelot key could not be determined because no key is tagged in file '+file)
                tkey = keyfinder_scan(file)
                if isinstance(tkey, Exception):
                    print(format_error(tkey))
                    error_dict[file] = tkey
                    continue
                else:
                    ckey = return_camelotkey(tkey)
        print(format_conf('Writing camelot key tag ')+format_val(ckey)+format_conf(' to ') + format_val(file))
        
        tags_obj = write_alt_key(tags_obj,ckey,'camelotkey') 
    else:
        pass
    
    if tag_playlist == 'y' or not tag_playlist:
        #print("tags_obj: ", tags_obj)
        try:
            pkey = return_playlistkey(tkey)
        except Exception as e:
            tkey = find_existing_keytags(tags_obj)
            if tkey != False:
                pkey = return_playlistkey(tkey)
            elif tkey == False:
                print('Playlist key could not be determined because no key is tagged in file '+file)
                tkey = keyfinder_scan(file)
                if isinstance(tkey, Exception):
                    print(format_error(tkey))
                    error_dict[file] = tkey
                    continue
                else:
                    pkey = return_playlistkey(tkey)
        print(format_conf('Writing playlist key tag ')+format_val(pkey)+format_conf(' to ') + format_val(file))
        
        tags_obj = write_alt_key(tags_obj,pkey,'playlistkey')
    else:
        pass
    
    if analyze_bpm_option == 'a':
        #aubio cannot analyze bpm if file not in wav format
        bpm = analyze_bpm(file)
        if bpm != False:
            print(format_conf('Writing BPM ')+format_val(bpm)+format_conf(' to ')+format_val(file))
            tags_obj = write_bpm(tags_obj,bpm,'bpm')
        else:
            continue
    
    if analyze_bpm_option == 'b' or not analyze_bpm_option or (analyze_bpm_option == 'c' and repitch_keys != 'n'):
        try:
            bpm = return_bpm(tags_obj)
        except Exception as e:
            print('No BPM found on file')
            bpm = analyze_bpm(file)
            if bpm != False:
                print(format_conf('Writing BPM ')+format_val(bpm)+format_conf(' to ')+format_val(file))
                tags_obj = write_bpm(tags_obj,bpm,'bpm')
            else:
                pass
    elif analyze_bpm_option == 'c' and repitch_keys != 'n':
        #repitch_keys must be 'n' since if yet, bpm option
        pass
    
    if repitch_keys == 'y' or not repitch_keys:
        #print(tags_obj)
        if len(freq_list) == 0:
            compile_freqs_to_list()
        
        tkey = find_existing_keytags(tags_obj)
        try:
            bpm = return_bpm(tags_obj)
        except Exception:
            bpm = None
        if not tkey or not bpm:
            print(format_warning('Skipping repitched keys for ')+format_val(file)+format_warning(': needs both a key and a BPM'))
            bpm_list_for_file = []
        else:
            bpm_list_for_file = bpm_list
        f = return_freq(tkey) if tkey else None
        #print('bpm ',bpm)
        #print('bpm type ',type(bpm))
        for desired_bpm in bpm_list_for_file:
            #calc_new_key(original_bpm, original_freq, desired_bpm)
            new_freq = calc_new_freq(bpm, f, desired_bpm)
            #print('newfreq ',new_freq)
            
            nearest_freq = find_nearest_number(new_freq)
            
            #major and minor keys on the same root share frequencies, so pick the
            #entry whose mode matches the track (camelot A = minor, B = major).
            #previously a minor track landing on C, G or D got the major key.
            mode = 'A' if tkey[-1] == 'm' else 'B'
            for k,v in key_dict.items():
                if nearest_freq in v[-1] and v[1][-1] == mode:
                    repitched_camelot_key = v[1]
                    break
            print(format_conf('Writing camelot key ')+format_val(repitched_camelot_key)+format_conf(' at bpm ')+format_val(desired_bpm)+format_conf(' to ')+format_val(file))
            tags_obj = write_alt_key(tags_obj,repitched_camelot_key,'repitchedcamelot_'+str(desired_bpm))
            
    try:
        if tags_obj_compare != tags_obj:
            tags_obj.save()
            shutil.move(file, './'+destdir)
            tagged_count+=1
        else:
            print(format_warning('No changes were made to ')+format_val(file))
            pass
    except Exception as e:
        print(format_error(e))
        error_dict[file] = e
        continue
else:
    for leftover in list(wav_cache):
        clear_wav(leftover)
    print(format_conf('\nTagging complete. ')+format_val(tagged_count)+format_conf(' tagged files can be found in ./'+destdir+'.\n'))
    if len(error_dict) != 0:
        print(format_val(len(error_dict)) + format_conf(" files encountered errors and were not tagged:"))
        print(format_error(error_dict))
