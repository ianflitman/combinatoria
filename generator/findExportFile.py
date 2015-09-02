__author__ = 'ian'

import os
from lxml import etree

path = "/media/ian/TOSHIBA EXT1/jane/exports/bs/n/P2/CONTENTS/CLIP"

def search(filename):

    found = False

    for file in os.walk(path):
        files = file[2]

    for file in files:
        if '.XML' in file:
            name = etree.parse(path + '/' + file).getroot()[0][5][0].text
            if name == filename:
                return True, etree.parse(path + '/' + file).getroot()[0][0].text


    return found, None


result, file = search('bleeds_ca')
pass