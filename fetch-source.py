import requests
import os
import sys
import subprocess

real_print = print
def print(*args):
    real_print(*args, file=sys.stderr, flush=True)

try:
    print('Creating directory for sources')
    os.mkdir('/source')
except FileExistsError:
    print('Directory for sources already exists?!')

try:
    print('Creating directory for audio sources')
    os.mkdir('/source-audio')
except FileExistsError:
    print('Directory for audio sources already exists?!')

url = 'https://crabrave.boringcactus.com/render?text=&ext=mp4&style='

styles = {'classic': 'classic', 'garfield': 'garfield', 'megalovania':'sans', 'otamatone':'otamatone'}

for source_style in styles:
    target_name = styles[source_style]
    print('Downloading source for style', source_style)
    size = 0
    with requests.get(url+source_style, stream=True) as inp:
        inp.raise_for_status()
        with open('/source/'+target_name+'.mp4', 'wb') as outp:
            for chunk in inp.iter_content(4096):
                outp.write(chunk)
                size += len(chunk)

    print('Downloaded style', source_style, 'used', size, 'bytes')
    print('Extracting audio for style', source_style)
    subprocess.Popen(['ffmpeg', '-i', '/source/'+target_name+'.mp4', '/source-audio/'+target_name+'.opus'])
    print('Audio extraction completed for style', source_style)
