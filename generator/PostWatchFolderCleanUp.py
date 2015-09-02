__author__ = 'ian'

import os
from lxml import etree
from io import StringIO

from lxml.etree import tostring

baseurl = '/media/ian/TOSHIBA EXT1/jane/exports/'
#path = "/media/ian/TOSHIBA EXT1/jane/exports/eieo/f/P2/CONTENTS/VIDEO/Source"
#restore_path = "/media/ian/TOSHIBA EXT1/jane/exports/eieo/f/P2/CONTENTS/VIDEO/"

#mp4_path = "/media/ian/TOSHIBA EXT1/jane/exports/eieo/f/web"
#P2_clip_path = "/media/ian/TOSHIBA EXT1/jane/exports/eieo/f/P2/CONTENTS/CLIP/"

class PostWatchClean:

    def __init__(self, conversation):
        for part in ['t']:
            conversation_part = conversation + '/' + part
            self.path = (baseurl + conversation_part + '/P2/CONTENTS/VIDEO/Source')
            self.restore_path = (baseurl + conversation_part + '/P2/CONTENTS/VIDEO/')
            self.mp4_path = (baseurl + conversation_part + '/web')
            self.P2_clip_path = (baseurl + conversation_part + '/P2/CONTENTS/CLIP/')
            self.moveP2Back()
            self.renameMP4Exports()


    def moveP2Back(self):
        for root, dirs, files in os.walk(self.path):
            print dirs
            for name in dirs:
                dir_name = os.path.join(root, name) + '/'
                print(dir_name)
                for files in os.walk(os.path.join(root, name)):
                    print files[2][0]
                    os.rename(dir_name + files[2][0], self.restore_path + files[2][0])
                    os.rmdir(dir_name)




    def renameMP4Exports(self):
        for root, dirs, files in os.walk(self.mp4_path):
            print files
            for file in files:
                fileroot_name = file[0:file.index('.mp4')] + '.XML'
                mp4_mxf_name =  file[0:file.index('.mp4')] + '.mp4'
                print fileroot_name
                try:
                    clip_name = etree.parse(self.P2_clip_path + fileroot_name).getroot()[0][5][0].text + '.mp4'
                except:
                    raise Exception('Exception - self.mp4_path: {0}, mp4_mxf_name: {1}, fileroot_name: {2}'.format(self.mp4_path, mp4_mxf_name, fileroot_name ))
                print (clip_name)
                os.rename(self.mp4_path + '/' + mp4_mxf_name, self.mp4_path + '/' + clip_name)


process_conversation = PostWatchClean('ff')


#moveP2Back()
#renameMP4Exports()








