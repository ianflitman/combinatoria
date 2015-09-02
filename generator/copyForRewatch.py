__author__ = 'ian'

import os
import shutil

source_path = "/media/ian/TOSHIBA EXT1/jane/exports/sc/f/P2/CONTENTS/"
copy_root = "/media/ian/TOSHIBA EXT1/jane/exports/rewatch/sc/f/"

#files_rewatch = ['00013B', '00013D', '00013M', '00013Q', '000138', '000145', '000145', '00014T', '000151','00015M', '00015Y', '000168', '000160', '000170']
#no file 0013M
#files_rewatch = ['00013Q', '000138', '000145', '000145', '00014T', '000151','00015M', '00015Y', '000168', '000160', '000170']
#no file 000160
#files_rewatch = ['000170']
#files_rewatch = ['00013B', '00013D', '00013Q', '000138', '000145', '000145', '00014T', '000151','00015M', '00015Y', '000168', '000170']
files_rewatch = ['00016O', '00013H']

def mkfolders():
    os.makedirs(copy_root + 'CONTENTS')
    for dir in ['AUDIO', 'CLIP', 'ICON', 'PROXY', 'VIDEO', 'VOICE']:
        os.makedirs(copy_root + 'CONTENTS/' + dir)

def copyfiles():
    for file in files_rewatch:
        shutil.copy(source_path + 'VIDEO/' + file + '.MXF', copy_root + 'CONTENTS/VIDEO')
        shutil.copy(source_path + 'CLIP/' + file + '.XML', copy_root + 'CONTENTS/CLIP')
        shutil.copy(source_path + 'CLIP/' + file + '.XMP', copy_root + 'CONTENTS/CLIP')
        shutil.copy(source_path + 'AUDIO/' + file + '00.MXF', copy_root + 'CONTENTS/AUDIO')
        shutil.copy(source_path + 'AUDIO/' + file + '01.MXF', copy_root + 'CONTENTS/AUDIO')
        shutil.copy(source_path + 'ICON/' + file + '.BMP', copy_root + 'CONTENTS/ICON')


#mkfolders()
copyfiles()