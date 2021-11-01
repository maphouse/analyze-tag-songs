from glob import glob
import os
import shutil
import ffmpeg
import keyfinder
from mutagen.id3 import ID3
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
    '16':[['Db','C#','Dbm'],'3B'],
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
        if f.split('.')[-1] == 'wav':
            output = ffmpeg.output(i,'.'.join(f.split('.')[:-1])+ext,acodec=acodec)
        elif f.split('.')[-1] == 'm4a':
            output = ffmpeg.output(i,'.'.join(f.split('.')[:-1])+ext,acodec=acodec, ab=ab)
            
        output.run()
    except Exception as e:
        print(format_error(e))
        print('ffmpeg encountered an error. Skipping conversion for '+file)
        return
    else:
        print(file+' converted successfully, deleting original.')
        os.remove(file)
    
#function searches all tags in file that could already contain a key
def find_existing_keytags(f):
    
    if f[-4:] == 'flac':
        tags_obj = FLAC(f)
        possible_keytags = ['key','initialkey']
    elif f[-3:] == 'mp3':
        tags_obj = ID3(f)
        possible_keytags = ['TKEY','TKE','TXXX:initialkey','TXXX:KEY']
            
        
    while True:
        for i,keytag in enumerate(possible_keytags):
            try:
                key = tags_obj[keytag][0]
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
    key_obj = keyfinder.key(f)
    print('Detected key '+key_obj.standard())
    return key_obj.standard()

def return_playlistkey(k):
    for playlistkey, keys in key_dict.items():
        if k in keys[0]:
            return playlistkey
        else:
            pass
        
def return_camelotkey(k):
    for keycode, keys in key_dict.items():
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
        id3.add(TXXX(encoding=3, text=k, desc='KEY'))
        return id3
    elif f[-3:] == 'wav':
        id3 = WAVE(f)
        id3.add(TKEY(encoding=3, text=k))


#write either camelot or playlist (t) key (k) to file or tag object (f)
def write_alt_key(f,k,t):
    if isinstance(f,ID3):
        #print('tagging mp3')
        f.add(TXXX(encoding=3, text=k, desc=t))
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
    print(format_question('Choose how to proceed with ')+format_underline('melodic key tags'))
    keyscan_option = input(format_question('[a] Scan all and overwrite existing key tags\n[b] Scan all and manually approve each overwrite\n[c] Only scan and tag files with missing key tags (default)\n'))
    if keyscan_option in ['a','b','c','']:
        break
while True:
    tag_camelot = input(format_question('Apply/Overwrite ')+format_underline('Camelot tags')+format_question(' to files? ([y]/[n])\n'))
    if tag_camelot in ['y','','n']:
        break
while True:
    tag_playlist = input(format_question('Apply/Overwrite ')+format_underline('Playlist tags')+format_question(' to files? (these are custom-defined codes that - when used to order songs in ascending or descending order - minimize tonal dissonance between songs during playback) ([y]/[n])\n'))
    if tag_playlist in ['y','','n']:
        break


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
error_dict = {}


for file in track_list:
    
    print('')
    
    #catch any missing metadata headers
    if file[-4:] == 'flac':
        pass
    elif file[-3:] == 'mp3':
        try:
            error_check = ID3(file)
        except Exception as e:
            print(format_error(e))
            error_dict[file] = e
            continue
    
    #make sure to not back up a file that has already been backed up during conversion
    if '.'.join(file.split('.')[:-1]) not in backed_up_list:
        backup(file)

    if keyscan_option == 'a':
    
        tkey = keyfinder_scan(file)
        print('Writing detected key tag '+tkey+' for ' + file)
        #file here
        tags_obj = write_key(file,tkey)
        
    elif keyscan_option == 'b':
        
        #file here
        tkey = find_existing_keytags(file)
        
        #tkey = id3['TKEY'][0]
        if tkey != False:
            keyscan_run = input(format_val(file) + format_question(' already contains key tag ') + format_val(tkey) + format_question(', do you want to run keyfinder anyway? ([y]/[n])\n'))
            if keyscan_run == 'y' or not keyscan_run:
                key = keyfinder_scan(file)
                if tkey != key:
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
            print(format_conf('Writing key tag ')+format_val(key)+format_conf(' to ') + format_val(file))
            #file here
            tags_obj = write_key(file,tkey)
            tkey = key
            
    elif keyscan_option == 'c' or not keyscan_option:
    
        tkey = find_existing_keytags(file)
        if tkey != False:
            print(file + ' key already tagged with '+tkey+'.')
            #distribute detected key tag anyway to other key tags (to account for inconsistent reading of ID3 tags in media players)
            tags_obj = write_key(file,tkey)
        elif tkey == False:
            print('Did not detect a key tag for '+file)
            key = keyfinder_scan(file)
            print(format_conf('Writing key tag ')+format_val(key)+format_conf(' to ') + format_val(file))
            tags_obj = write_key(file,key)
            tkey = key
            
            #id3.add(COMM(encoding=3, text='key tag '+key.standard()+' written using libKeyFinder.'))     
    #elif keyscan_option == 'd':
    #    print('No keys were scanned for '+file)
    
    
    if tag_camelot == 'y' or not tag_camelot:
        try:
            ckey = return_camelotkey(tkey)
        #exception will only occur if [d] was selected in melodic key question
        except Exception as e:
            tkey = find_existing_keytags(file)
            if tkey != False:
                ckey = return_camelotkey(tkey)
            elif tkey == False:
                print('Camelot key could not be determined because no key is tagged in file '+file)
                tkey = keyfinder_scan(file)
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
            tkey = find_existing_keytags(file)
            if tkey != False:
                pkey = return_playlistkey(tkey)
            elif tkey == False:
                print('Playlist key could not be determined because no key is tagged in file '+file)
                tkey = keyfinder_scan(file)
                pkey = return_camelotkey(tkey)
        print(format_conf('Writing playlist key tag ')+format_val(pkey)+format_conf(' to ') + format_val(file))
        
        tags_obj = write_alt_key(tags_obj,pkey,'playlistkey')
    else:
        pass
    
    tags_obj.save()
    shutil.copy(file, './'+destdir)
    os.remove(file)
else:
    print(format_conf('\nTagging complete. Tagged files can be found in ./'+destdir+'.\n'))
    if len(error_dict) != 0:
        print(format_val(len(error_dict)) + format_conf(" files encountered errors and were not tagged:"))
        print(format_error(error_dict))