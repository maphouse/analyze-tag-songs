from glob import glob
import os
import shutil
import ffmpeg
import keyfinder
import subprocess
from shlex import join
from math import trunc
from mutagen.id3 import ID3
from mutagen.id3 import TKEY
from mutagen.id3 import TKE
from mutagen.id3 import TXXX
from mutagen.id3 import TBPM
from mutagen.id3 import COMM
from mutagen.flac import FLAC
#from extract_bpm import get_file_bpm

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

#'playlist key':[['theoretical key options'...],'camelot key']

key_dict = {
    '1':[['C'],'8B'],
    '2':[['Am'],'8A'],
    '3':[['Em'],'9A'],
    '4':[['G'],'9B'],
    '5':[['D'],'10B'],
    '6':[['Bm'],'10A'],
    '7':[['F#m','Gbm'],'11A'],
    '8':[['A'],'11B'],
    '9':[['E'],'12B'],
    '10':[['Dbm'],'12A'],
    '11':[['Abm'],'1A'],
    '12':[['B'],'1B'],
    '13':[['F#','Gb'],'2B'],
    '14':[['Ebm'],'2A'],
    '15':[['Bbm'],'3A'],
    '16':[['Db','C#'],'3B'],
    '17':[['Ab','G#'],'4B'],
    '18':[['Fm'],'4A'],
    '19':[['Cm'],'5A'],
    '20':[['Eb','D#'],'5B'],
    '21':[['Bb','A#'],'6B'],
    '22':[['Gm'],'6A'],
    '23':[['Dm'],'7A'],
    '24':[['F'],'7B']
}

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

#function for quick conversion of mp3 to wav for sole purpose of analyzing bpm
def convert_mp3_to_wav(f):
    filename = '.'.join(f.split('.')[:-1])
    ext = '.wav'
    print(format_conf('Converting ')+format_val(f)+format_conf(' to ')+format_val(ext)+format_conf(' to analyze BPM.'))
    i = ffmpeg.input(f)
    try:
        output = ffmpeg.output(i,filename+ext)
        output.run()
    except Exception as e:
        print(format_error(e))
        print('ffmpeg encountered an error. Skipping conversion for '+file)
        return False,e
    else:
        print(f+' converted successfully')
        return filename+ext
        
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

def keyfinder_scan(f):
    print('Running keyfinder on '+f)
    try:
        key_obj = keyfinder.key(f)
        print('Detected key '+key_obj.standard())
        return key_obj.standard()
    except Exception as e:
        return e

def return_bpm(f: 'mutagen') -> int:
    #print(type(f))
    if isinstance(f,ID3):
        #print('f ',f)
        #print('f bpm ',f['TBPM'][-1])
        #print('f bpm type ',type(f['TBPM'][-1]))
        return int(float(f['TBPM'][-1]))
    elif isinstance(f,FLAC):
        return int(float(f['bpm'][-1]))

#do not use outside this script since function depends on other funtions here if f is not wav
#this function converts to wav (if not wav) and analyzes for bpm and returns a bpm int, it also deletes the temporary wav that was created if it had to perform conversion
def analyze_bpm(f):
    if f[-3:] != 'wav':
        converted = convert_mp3_to_wav(file)
        if isinstance(converted,tuple):
            if  converted[0] == False:
                print('Cannot analyze BPM for '+file)
                print('Skipping')
                error_dict[f] = converted[1]
                return False
        else:
            print('converted to '+converted)
    else:
        pass
    try:
        #using Popen (from subprocess) and join (from shlex)
        aubio_shell_command = subprocess.Popen(join(['aubio','tempo',converted]), stdout=subprocess.PIPE, shell=True)
        bpm = float(''.join(c for c in str(aubio_shell_command.communicate()[0]) if (c.isdigit() or c == '.')))
        #bpm = get_file_bpm(converted)
        print("BPM detected: ",bpm)
        bpm = str(trunc(bpm))
    except Exception as e:
        print(format_error(e))
        print('bpm analysis encountered an error. Skipping analysis for '+f)
        error_dict[f] = e
        return False
    os.remove(converted)
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

# conventions are based on https://exiftool.org/TagNames/ID3.html but many applications use TXXX:[descriptor] as well
def write_key(f,k):
    if f[-4:] == 'flac':
        flac = FLAC(f)
        flac["key"] = k
        flac["initialkey"] = k
        return flac
    elif f[-3:] == 'mp3':
        id3 = ID3(f)
        id3.add(TKEY(encoding=3, text=k))
        id3.add(TKE(encoding=3, text=k))
        id3.add(TXXX(encoding=3, text=k, desc='initialkey'))
        id3.add(TXXX(encoding=3, text=k, desc='key'))
        #remove any extra id3 tags that don't meet conventions.
        tags_to_remove = ['TXXX:INITIALKEY','TXXX:KEY']
        for t in tags_to_remove:
            try:
                id3.pop(t)
            except:
                continue
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

#setup interview

while True:
    print(format_question('How do you wish to tag your files by ')+format_underline('musical key')+format_question('?\n'))
    keyscan_option = input(format_question('[a] Scan all and overwrite existing key tags\n[b] Scan all and manually approve each overwrite\n[c] Only scan and tag files with missing key tags (default)\n[d] Skip\n'))
    if keyscan_option in ['a','b','c','d','']:
        break
while True:
    tag_camelot = input(format_question('Apply/Overwrite ')+format_underline('Camelot tags')+format_question(' to files? ([y]/[n])\n'))
    if tag_camelot in ['y','','n']:
        break
while True:
    tag_playlist = input(format_question('Apply/Overwrite ')+format_underline('Playlist tags')+format_question(' to files? (these are custom-defined codes that - when used to order songs in ascending or descending order - minimize tonal dissonance between songs during playback) ([y]/[n])\n'))
    if tag_playlist in ['y','','n']:
        break
while True:
    analyze_bpm_option = input(format_question('[a] Analyze and overwrite ')+format_underline('BPM')+format_question('? ([y]/[n])\n[b] Analyze and write only missing ')+format_underline('BPM')+format_question(' values? (default)\n[c] Skip.\n'))
    if analyze_bpm_option in ['a','','c','b']:
        break
'''
while True:
    rename_files = input(format_question('Rename files according to the following format? ')+format_underline('%camelotkey%_%bpm%_%artist%_%title%'))
    if rename_files in ['y','','n']:
        break
'''

backed_up_list = []

wav_list = glob('*.wav')
if len(wav_list) > 0:
    while True:
        wav_conv_choice = input(format_val(len(wav_list))+format_question(' .wav files require conversion to be tagged. Unconverted files will be ignored. Convert to .flac? (y/n)'))
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
        m4a_conv_choice = input(format_val(len(m4a_list))+format_question(' .m4a files require conversion to be tagged. Unconverted files will be ignored. Convert to mp3? (y/n)'))
        if wav_conv_choice in ['y','n','']:
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
    
    #catch any missing metadata headers
    if file[-4:] == 'flac':
        tags_obj = FLAC(file)
        tags_obj_compare = FLAC(file)
    elif file[-3:] == 'mp3':
        try:
            tags_obj = ID3(file)
            tags_obj_compare = ID3(file)
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
        if len(tkey) > 3:
            print(format_error(tkey))
            error_dict[file] = tkey
            continue
        else:
            print('Writing detected key tag '+tkey+' for ' + file)
            #file here
            tags_obj = write_key(file,tkey)
        
    elif keyscan_option == 'b':
        
        #file here
        tkey = find_existing_keytags(tags_obj)
        
        #tkey = id3['TKEY'][0]
        if tkey != False:
            keyscan_run = input(format_val(file) + format_question(' already contains key tag ') + format_val(tkey) + format_question(', do you want to run keyfinder anyway? ([y]/[n])\n'))
            if keyscan_run == 'y' or not keyscan_run:
                key = keyfinder_scan(file)
                if len(key) > 3:
                    print(format_error(key))
                    error_dict[file] = key
                    continue
                elif tkey != key:
                    while True:
                        key_overwrite = input(format_val(file) + format_question(' already contains key tag ') + format_val(tkey) + format_question(' but keyfinder detected ') + format_val(key) + format_question('. Overwrite? ([y]/[n])'))
                        if key_overwrite in ['y','n','']:
                            break
                    if key_overwrite == 'y' or not key_overwrite:
                        print(format_conf('Overwriting key tags for ') + format_val(file))
                        #file here
                        tags_obj = write_key(file,key)
                        #id3.add(COMM(encoding=3, text='key tag '+tkey+' overwritten using libKeyFinder to '+key.standard()))
                    else:
                        print('No changes were made to key tag')
                        #distribute detected key tag anyway to other key tags (to account for inconsistent reading of ID3 tags in media players)
                        #file here
                        tags_obj = write_key(file,tkey)
                else:
                    print('keyfinder detected same key.')
                    print(format_conf('Overwriting key tags for ') + format_val(file))
                    #file here
                    tags_obj = write_key(file,key)
            else:
                print('No changes were made to key tag')
                #distribute detected key tag anyway to other key tags (to account for inconsistent reading of ID3 tags in media players)
                #file here
                tags_obj = write_key(file,tkey)
        elif tkey == False:
            print('Did not detect a key tag for '+file)
            key = keyfinder_scan(file)
            if len(key) > 3:
                print(format_error(key))
                error_dict[file] = key
                continue
            else:
                print(format_conf('Writing key tag ')+format_val(key)+format_conf(' to ') + format_val(file))
                #file here
                tags_obj = write_key(file,key)
                tkey = key
            
    elif keyscan_option == 'c' or not keyscan_option:
        tkey = find_existing_keytags(tags_obj)
        if tkey != False:
            print(file + ' key already tagged with '+tkey+'.')
            #distribute detected key tag anyway to other key tags (to account for inconsistent reading of ID3 tags in media players)
            tags_obj = write_key(file,tkey)
        elif tkey == False:
            print('Did not detect a key tag for '+file)
            key = keyfinder_scan(file)
            if len(key) > 3:
                print(format_error(key))
                error_dict[file] = key
                continue
            else:
                print(format_conf('Writing key tag ')+format_val(key)+format_conf(' to ') + format_val(file))
                tags_obj = write_key(file,key)
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
                if len(tkey) > 3:
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
                if len(tkey) > 3:
                    print(format_error(tkey))
                    error_dict[file] = tkey
                    continue
                else:
                    pkey = return_camelotkey(tkey)
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
    
    if analyze_bpm_option == 'b' or not analyze_bpm_option:
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
    elif analyze_bpm_option == 'c':
        #repitch_keys must be 'n' since if yet, bpm option
        pass
            
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
    print(format_conf('\nTagging complete. ')+format_val(tagged_count)+format_conf(' tagged files can be found in ./'+destdir+'.\n'))
    if len(error_dict) != 0:
        print(format_val(len(error_dict)) + format_conf(" files encountered errors and were not tagged:"))
        print(format_error(error_dict))
