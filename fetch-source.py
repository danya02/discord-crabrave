import requests
import os

try:
    print('Creating directory')
    os.mkdir('/source')
except FileExistsError:
    print('Directory already exists')

url = 'https://crabrave.boringcactus.com/render?text=&ext=mp4&style='

styles = {'classic': 'classic', 'garfield': 'garfield', 'megalovania':'sans', 'otamatone':'otamatone'}

for source_style in styles:
    print('Downloading source for style', source_style)
    size = 0
    with requests.get(url+source_style, stream=True) as inp:
        inp.raise_for_status()
        with open('/source/'+styles[source_style]+'.mp4', 'wb') as outp:
            for chunk in inp.iter_content(4096):
                outp.write(chunk)
                size += len(chunk)

    print('Downloaded style', source_style, 'used', size, 'bytes')
