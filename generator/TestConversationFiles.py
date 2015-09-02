__author__ = 'ian'

from lxml import etree
import logging
import time
import os.path
from subprocess import Popen, PIPE, call
from pipes import quote


janeXMLPath = '/media/ian/OS/Users/ianflitman/Desktop/Jane.xml'
fileRootPath = '/media/ian/TOSHIBA EXT1/jane/exports/'
P2ClipPath = 'P2/CONTENTS/CLIP'
ffmpeg_exec = "/opt/jane_ng/jane_nodejs/ffmpeg-git-20150308-64bit-static/ffmpeg"


class FileChecker():

    def __init__(self, code, tolerance=0.1):

        self.code = code
        self.tolerance = tolerance
        self.baselogDir = os.path.dirname(os.path.abspath(__file__)) + '/tests/' + self.nameStr() #'/tests/' + self.code + '_tolerance_' + str(self.tolerance) + '_' + time.strftime("%d/%m/%Y").replace('/', '-')
        if not os.path.isdir(self.baselogDir):
            try:
                os.makedirs(self.baselogDir)
            except:
                raise Exception('error while making directory:{0}'.format(self.baselogDir))

        self.log = self.baselogDir + '/' + self.nameStr() + '.log' #'_tolerance_' + str(self.tolerance) + '_' + time.strftime("%d/%m/%Y").replace('/', '-')
        logging.basicConfig(filename=self.log, level=logging.DEBUG)
        self.xml = etree.parse(janeXMLPath).getroot()
        self.scene = self.xml.find('./conversation[@title="{0}"]'.format(self.code))
        self.parts = self.scene.findall('./section')
        self.failures = 0
        self.webfilePath = ''
        self.suspectDurationFiles = []

        self.checkFiles()
        self.concatSuspectDurationFiles()

    def nameStr(self):
        return self.code + '_tolerance_' + str(self.tolerance) + '_' + time.strftime("%d/%m/%Y").replace('/', '-')

    def checkFiles(self):
        for counter, part in enumerate(self.parts, start=1):
            keyword = part.attrib['keyword']
            self.webfilePath = fileRootPath + self.code + '/' + keyword + '/web/'
            cuts = part.findall('./cut')
            for cut in cuts:
                cutType = cut.attrib['type']

                if cutType == 'pause':
                    self.checkNode(cut)
                elif cutType == 'default':
                    self.checkNode(cut)
                elif cutType == 'alternative':
                    self.filterAlternative(cut, cut.attrib['alt'])
                else:
                    raise Exception('cutType {0} has no processing function as yet'.format(cutType))

    def filterAlternative(self, cut, kind):
        if kind == 'free':
            self.checkAlternative(cut)
        elif kind == 'paired':
            self.checkAlternative(cut)
        elif kind == 'paired parent':
            self.checkParent(cut)
        elif kind  == 'parent':
            self.checkParent(cut)
        elif kind == 'weekday':
            self.checkAlternative(cut)
        elif kind == 'paired mixed':
            self.checkAlternative(cut)
            self.checkNested(cut)
        elif kind == 'compound':
            self.checkNode(cut.find('./default'))
            self.checkAlternative(cut)
        elif kind == 'paired nested':
            self.checkParent(cut)
        elif kind == 'loop':
            self.checkParent(cut)
        elif kind == 'multifree':
            self.checkAlternative(cut)
        elif kind == 'speaker':
            self.checkSpeakerAlternative(cut)
        elif kind == 'double':
            self.checkAlternative(cut)
        else:
            raise Exception("Alternative type '{0}' has no processing function as yet".format(kind))


    def checkNode(self, cut):
        try:
            basename = cut.find('./name').text + '_'
        except:
            raise Exception('error on cut')
        shots = cut.findall('./shots/angle')
        for angle in shots:
            filename = basename + angle.attrib['type'] + '.mp4'
            filepath = self.webfilePath + filename
            try:
                duration = float(angle.attrib['length'])
            except:
                raise Exception('error on length attribute for {0}'.format(filename))
            self.checkFileExists(filepath, duration)


    def checkNested(self, cut):
        nested = cut.find('./nested')
        nested_kind = nested.attrib['alt']
        self.filterAlternative(nested, nested_kind)


    def checkAlternative(self, cut):
        options = cut.findall('./option')
        for option in options:
            self.checkNode(option)


    def checkParent(self, cut):
        alts = cut.findall('./alternative')
        for alt in alts:
            child_kind = alt.attrib['alt']
            self.filterAlternative(alt, child_kind)
            #self.checkAlternative(alt)


    def checkFileExists(self, filepath, duration):
        if os.path.exists(filepath):
            logging.info('Found: {0}'.format(filepath))
            self.checkDuration(filepath, duration)
        else:
            logging.warn('\n\tMissing: {0}\n'.format(filepath))
            self.failures += 1


    def checkDuration(self, filepath, duration):
        p = Popen(['MP4Box', '-info', filepath], stdout=PIPE)
        out, err = p.communicate()
        durationStr = out[out.index('Duration'): out.index('Fragmented')]
        realDuration = float(durationStr[durationStr.index('.')-2:])
        timeDiff = abs(duration-realDuration)
        logging.info('time diff {0}'.format(timeDiff))

        if timeDiff > self.tolerance:
            logging.warn('\n\tDuration Mismatch on {0}. \n\tExpected: {1}. \n\tGot: {2} \n\tDiff: {3}\n'.format(filepath, duration, realDuration, timeDiff))
            self.suspectDurationFiles.append(filepath)
            fileStr = 'file\t' + filepath.replace(' ', '\ ') + '\'' + '\n'
            print fileStr

    def checkSpeakerAlternative(self, cut):
        kind = cut[0].tag
        print kind
        if kind == 'default':
            defaults = cut.findall('./default')
            for default in defaults:
                self.checkNode(default)
        elif kind == 'alternative':
            self.checkParent(cut)
        else:
            raise Exception("speaker type alternative is not either default or alternative. It is {0}".format(kind))
        pass


    def concatSuspectDurationFiles(self):
        concatFile = self.baselogDir + '/concat.txt'
        movieFile = self.baselogDir + '/' + self.nameStr() + '.mp4'
        f = open(concatFile, 'w')
        for file in self.suspectDurationFiles:
            f.write('file\t' + file.replace(' ', '\ ') + '\'' + '\n')
        f.close()

        call([ffmpeg_exec, '-f', 'concat', '-i', concatFile, '-c', 'copy', '-y', movieFile])


filechecker = FileChecker('ff', 0.1)


