__author__ = 'ian'
import xml.etree.ElementTree as etree

class FileTest:

    def __init__(self, conversation):
        self.xml = etree.parse('/opt/combinatoria/xml/Jane.xml')
        self.code = conversation
        self.scene = self.xml.find('./conversation[@title="{0}"]'.format(conversation))
        self.parts = self.scene.findall('./section')
        self.files = []
        self.getFilesListed()



    def getFilesListed(self):
        for part_counter, part in enumerate(self.parts):
            print 'part found'
            shots = part[0].findall('./shots/angle')
            for shot in shots:
                filename = 'pause_' + self.code + '_' + self.parts[part_counter].attrib['keyword'] + '_' + shot.attrib['type']
                length = shot.attrib['length']
                print filename
                print length
                self.files.append({'file': filename, 'length': length})

            for cut in part[1:]:
                type = cut.attrib['type']
                if type == 'default':
                    self.processElement(cut)
                    #angles = cut.findall('./shots/angle')
                    #name = cut.find('./name').text
                    #for angle in angles:
                    #    print name + '_' + angle.attrib['type']
                    #    print angle.attrib['length']
                elif type == 'alternative':
                    options = cut.findall('./option')
                    for option in options:
                        self.processElement(option)
                    print 'alt found'
                pass
        pass

    def processElement(self, element):
         angles = element.findall('./shots/angle')
         name = element.find('./name').text
         for angle in angles:
            print name + '_' + angle.attrib['type']
            print angle.attrib['length']
            pass

FileTest('mtl')