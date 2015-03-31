__author__ = 'ian'

import xml.etree.ElementTree as etree
import json

class XMLToJson(object):

    def __init__(self, filename, code):
        self.filename = filename
        self.code = code
        self.cuts = []
        self.cut_index = 0
        self.part_index = -1
        self.xml = etree.parse(filename).getroot()
        self.dict = self.xml[1]
        self.json = {'meta': {'script': 'Jane',
                              'act': 'conversations',
                              'mimetype': 'mp4'},
                     'scene': {'name': "",
                               'code': code,
                               'parts': []}}
        self.scene = self.xml.find('./conversation[@title="{0}"]'.format(code))
        self.parts = self.scene.findall('./section')
        self.json['scene']['name'] = self.dict_value(self.scene.attrib['title'])
        self.process()

    def process(self):
        for part in self.parts:
            self.part_index += 1
            self.json['scene']['parts'].append({'keyword': part.attrib['keyword'], 'summary': part.attrib['summary'], 'content': []})
            for cut in part:
                self.branch(cut)

    def branch(self, cut, isChild=False):
        type_name = cut.attrib['type']
        self.cut_index += 1
        #print type_name
        if type_name == 'pause':
            self.process_sequence_set(cut)
        elif type_name == 'default':
            self.process_default(cut)
        elif type_name == 'alternative':
            self.process_alternative_free(cut, isChild)
        elif type_name == 'ALTERNATIVE_PAIRED_MIXED':
            pass
        else:
            print('name not recognised in branch(): {0}'.format(type_name))

    def sort_alternatives(self, cut):
        alt_type = cut.attrib['alt']
        if alt_type == 'alt':
            self.process_alternative_free(cut)
        elif alt_type == 'compound':
            self.process_compund(cut)
        elif alt_type == 'paired':
            self.process_paired(cut)
        elif alt_type == 'paired_parent':
            self.process_paired_parent(cut)

    def getCurrentId(self):
        return self.code + '_' + str(self.cut_index)

    def process_sequence_set(self, cut):
        id_value = self.getCurrentId()
        set_seq_content = {'id': id_value, 'type': 'SEQUENCE_SET', 'line': 'Pause', 'sets': [{'name': 'short', 'seqs':[]}, {'name': 'medium', 'seqs': []}, {'name': 'long', 'seqs': []}]}

        sets = cut.findall('./sequence')
        for seq_type_counter, seq_type in enumerate(sets):
            seqs = seq_type.text.split(',')

            for seqlist in seqs:
                seq_content = []
                seqlist = seqlist.replace('+', ',')
                seq = seqlist.split(',')
                for shot in seq:
                    angle = cut.find('./shots/angle[@type="{0}"]'.format(shot))
                    duration = angle.attrib['length']
                    filename = 'pause_' + self.code + '_' + self.parts[self.part_index].attrib['keyword'] + '_' + shot
                    seq_content.append({'file': filename, 'duration': duration})

                set_seq_content['sets'][seq_type_counter]['seqs'].append(seq_content)

        self.json['scene']['parts'][self.part_index]['content'].append(set_seq_content)
        print(json.dumps(self.json))

        pass

    def process_default(self, cut, isChild=False):
        source_content = []
        line = cut.find('./line').text
        speaker = cut.attrib['speaker']
        id_value = self.getCurrentId()
        name = cut.find('./name').text

        sources = cut.findall('./shots/angle')
        for source in sources:
            duration = source.attrib['length']
            filename = name + '_' + source.attrib['type']
            source_content.append({'file': filename, 'duration': duration})

        default_content = {'id': id_value, 'line': line, 'speaker': speaker, 'type': 'DEFAULT', 'sources': source_content}

        if isChild is False:
            self.json['scene']['parts'][self.part_index]['content'].append(default_content)

        print(json.dumps(self.json))



    def process_alternative_free(self, cut, isChild):
        pass

    def process_compound(self, cut, isChild):
        pass

    def process_parent(self, cut):
        pass

    def process_paired(self, cut):
        pass

    def process_paired_parent(self, cut):
        pass

    def dict_value(self, code):
        return self.dict.find('item/.[@code="{0}"]'.format(code)).attrib['content']


    def dict_key(self, code):
        return self.dict.find('item/.[@content="{0}"]'.format(code)).attrib['code']


test = XMLToJson('/opt/combinatoria/xml/Jane.xml', 'mtl')

