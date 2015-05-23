__author__ = 'ian'

import os
from lxml import etree
from io import StringIO

from lxml.etree import tostring

path = "/media/ian/TOSHIBA EXT1/jane/exports/mtl/t/P2/CONTENTS/VIDEO/Source"
restore_path = "/media/ian/TOSHIBA EXT1/jane/exports/mtl/t/P2/CONTENTS/VIDEO/"

mp4_path = "/media/ian/TOSHIBA EXT1/jane/exports/test/web/t"
P2_clip_path = "/media/ian/TOSHIBA EXT1/jane/exports/mtl/t/P2/CONTENTS/CLIP/"


def moveP2Back():
    for root, dirs, files in os.walk(path):
        print dirs
        for name in dirs:
            dir_name = os.path.join(root, name) + '/'
            print(dir_name)
            for files in os.walk(os.path.join(root, name)):
                print files[2][0]
                os.rename(dir_name + files[2][0], restore_path + files[2][0])
                os.rmdir(dir_name)


def renameMP4Exports():
    for root, dirs, files in os.walk(mp4_path):
        print files
        for file in files:
            fileroot_name = file[0:file.index('.mp4')] + '.XML'
            mp4_mxf_name =  file[0:file.index('.mp4')] + '.mp4'
            print fileroot_name
            clip_name = etree.parse(P2_clip_path + fileroot_name).getroot()[0][5][0].text + '.mp4'
            print (clip_name)
            os.rename(mp4_path + '/' + mp4_mxf_name, mp4_path + '/' + clip_name)


moveP2Back()
renameMP4Exports()








