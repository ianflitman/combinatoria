__author__ = 'ian'

import xml.etree.ElementTree as etree
#from xml import tostring
from subprocess import Popen, PIPE
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
        self.json = {'scene': {'name': "",
                               'code': code,
                               'parts': []}}
        self.scene = self.xml.find('./conversation[@title="{0}"]'.format(code))
        self.parts = self.scene.findall('./section')
        self.json['scene']['name'] = self.dict_value(self.scene.attrib['title'])
        self.process()
        #self.print_to_file()

    def process(self):
        for part in self.parts:
            self.part_index += 1
            self.cut_index = 0
            self.json['scene']['parts'].append({'keyword': part.attrib['keyword'], 'summary': part.attrib['summary'], 'content': []})
            for cut in part:
                self.branch(cut)


    def branch(self, cut, isChild=False):
        type_name = cut.attrib['type']
        self.cut_index += 1

        if type_name == 'pause':
            self.process_sequence_set(cut)
        elif type_name == 'default':
            self.process_default(cut)
        elif type_name == 'alternative':
            self.sort_alternatives(cut)
        elif type_name == 'ALTERNATIVE_PAIRED_MIXED':
            pass
        else:
            raise Exception('name not recognised in branch(): {0}'.format(type_name))


    def sort_alternatives(self, cut):
        alt_type = cut.attrib['alt']
        if alt_type == 'free':
            self.process_alternative_free(cut)
        elif alt_type == 'compound':
            self.process_compound(cut)
        elif alt_type == 'paired':
            self.process_paired(cut)
        elif alt_type == 'paired_parent':
            self.process_paired_parent(cut)
        elif alt_type == 'parent':
            self.process_parent(cut)
        else:
            raise Exception('type not found in sort_alternative'.format(alt_type))


    def getCurrentId(self):
        return self.code + '_' + self.parts[self.part_index].attrib['keyword'] + '_'+ str(self.cut_index)


    def process_sequence_set(self, cut):
        #set_seq_content = {'id': self.getCurrentId(), 'type': 'SEQUENCE_SET', 'line': 'Pause', 'sets': [{'name': 'short', 'seqs':[]}, {'name': 'medium', 'seqs': []}, {'name': 'long', 'seqs': []}]}
        set_seq_content = {'type': 'SEQUENCE_SET', 'line': 'Pause', 'sets': [{'name': 'short', 'seqs':[]}, {'name': 'medium', 'seqs': []}, {'name': 'long', 'seqs': []}]}
        sets = cut.findall('./sequence')
        for seq_type_counter, seq_type in enumerate(sets):
            seqs = seq_type.text.split(',')

            for seqlist in seqs:
                seq_content = []
                seqlist = seqlist.replace('+', ',')
                seq = seqlist.split(',')
                for shot in seq:
                    angle = cut.find('./shots/angle[@type="{0}"]'.format(shot))
                    duration = float(angle.attrib['length'])
                    filename = 'pause_' + self.code + '_' + self.parts[self.part_index].attrib['keyword'] + '_' + shot
                    seq_content.append({'file': filename, 'duration': duration})

                set_seq_content['sets'][seq_type_counter]['seqs'].append(seq_content)

        self.json['scene']['parts'][self.part_index]['content'].append(set_seq_content)


    def process_default(self, cut, isChild=False):

        line = cut.find('./line').text
        speaker = cut.attrib['speaker']
        #id_value = self.getCurrentId()
        source_content = self.process_sources(cut)
        #default_content = {'id': id_value, 'line': line, 'speaker': speaker, 'type': 'DEFAULT', 'sources': source_content}
        default_content = {'line': line, 'speaker': speaker, 'type': 'DEFAULT', 'sources': source_content}

        if isChild is False:
            self.json['scene']['parts'][self.part_index]['content'].append(default_content)
        else:
            return default_content

    def process_alternative_free(self, cut, isChild=False):
        #alt_free_content = {'id': self.getCurrentId(), 'type': 'ALTERNATIVE_FREE', 'options': []}
        alt_free_content = {'type': 'ALTERNATIVE_FREE', 'options': []}
        alt_free_content['options'] = self.process_options(cut)

        if isChild is False:
            self.json['scene']['parts'][self.part_index]['content'].append(alt_free_content)
        else:
            return alt_free_content


    def process_sources(self, cut):
        source_content = []
        try:
            name = cut.find('./name').text
        except:
            pass

        sources = cut.findall('./shots/angle')
        for source in sources:
            duration = source.attrib['length']
            filename = name + '_' + source.attrib['type']
            source_content.append({'file': filename, 'duration': float(duration)})
            #self.get_duration(filename, duration)

        return source_content

    def process_options(self, cut):
        #alt_type = cut.attrib['alt']
        options = cut.findall('./option')
        option_vals = []

        for pos, option in enumerate(options, start=1):
            option_content = {}
            option_content['line'] = option.find('./line').text
            option_content['speaker'] = cut.attrib['speaker']
            option_content['position'] = pos
            option_content['sources'] = self.process_sources(option)
            option_vals.append(option_content)

        return option_vals


    def process_compound(self, cut, isChild=False):
        speaker = cut.attrib['speaker']
        default = cut.find('./default')
        default.attrib['speaker'] = speaker
        options = cut.findall('./option')
        #compound_content = {'id': self.getCurrentId(), 'default': self.process_default(default, True), 'options': self.process_options(cut), 'type': 'ALTERNATIVE_COMPOUND'}
        compound_content = {'default': self.process_default(default, True), 'options': self.process_options(cut), 'type': 'ALTERNATIVE_COMPOUND'}
        if isChild is False:
            pass
            print 'Not yet appending compound to self.json!'
        else:
            return compound_content


    def process_parent(self, cut):
        children = cut.findall('./alternative')
        speaker = cut.attrib['speaker']
        #parent_content = {'id': self.getCurrentId(), 'type': 'ALTERNATIVE_PARENT', 'children': self.process_children(children, speaker)}
        parent_content = {'type': 'ALTERNATIVE_PARENT', 'children': self.process_children(children, speaker)}
        self.json['scene']['parts'][self.part_index]['content'].append(parent_content)
        print(json.dumps(self.json))
        pass

    def process_children(self, children, speaker):
        child_content = []
        for count, child in enumerate(children, start=1):
            child_type = child.attrib['alt']
            child.attrib['speaker'] = speaker
            if child_type == 'free':
                alt_content = self.process_alternative_free(child, True)
                alt_content['position'] = count
                child_content.append(alt_content)
            elif child_type == 'compound':
                compound_content = self.process_compound(child, True)
                compound_content['position'] = count
                child_content.append(compound_content)
            else:
                print 'child type not caught or found in self.process_children()'

        return child_content


    def process_paired_args(self, cut):
        args = {}
        pos_str = cut.attrib['position']
        args['pos'] = int(pos_str[0: pos_str.index('_')])
        args['total'] = int(pos_str[pos_str.index('_') + 1:])

        if args['pos'] == 1 or args['pos'] < args['total']:
            args['next'] = cut.attrib['next']

        if args['pos'] > 1 and args['pos'] <= args['total']:
            #minus one to convert to index of array
            #prevStr = cut.attrib['previous']
            args['prev'] = cut.attrib['previous']

        return args

    def process_paired(self, cut):
        #paired_content = {'id': self.getCurrentId(), 'type': 'ALTERNATIVE_PAIRED', 'options': self.process_options(cut), 'arguments': self.process_paired_args(cut)}
        paired_content = {'type': 'ALTERNATIVE_PAIRED', 'options': self.process_options(cut), 'arguments': self.process_paired_args(cut)}
        self.json['scene']['parts'][self.part_index]['content'].append(paired_content)
        #print(json.dumps(self.json))
        pass

    def process_paired_parent(self, cut):
        children = cut.findall('./alternative')
        speaker = cut.attrib['speaker']

        #paired_parent_content = {'id': self.getCurrentId(), 'type': 'ALTERNATIVE_PAIRED_PARENT', 'children': self.process_children(children, speaker), 'arguments': self.process_paired_args(cut)}
        paired_parent_content = {'type': 'ALTERNATIVE_PAIRED_PARENT', 'children': self.process_children(children, speaker), 'arguments': self.process_paired_args(cut)}
        self.json['scene']['parts'][self.part_index]['content'].append(paired_parent_content)
        print(json.dumps(self.json))
        pass

    def dict_value(self, code):
        return self.dict.find('item/.[@code="{0}"]'.format(code)).attrib['content']


    def dict_key(self, code):
        return self.dict.find('item/.[@content="{0}"]'.format(code)).attrib['code']

    def print_to_file(self):
        json_file = open('../json/{0}.json'.format(self.code), 'w')
        json_file.write(json.dumps(self.json))
        json_file.close()
        pass

    def get_duration(self, filename, duration):
        filename = '/home/ian/Documents/Jane/mp4/web/' + self.code + '/' + self.parts[self.part_index].attrib['keyword'] + '/' + filename + '.mp4'
        p = Popen(['MP4Box', '-info', filename], stdout=PIPE)
        out, err = p.communicate()
        durationStr = out[out.index('Duration'): out.index('Fragmented')]
        file_duration = float(durationStr[durationStr.index('.')-2:])

        print 'xml duration {0} vs. MP4Box duration {1}'.format(duration, file_duration)

test = XMLToJson('/opt/combinatoria/xml/Jane.xml', 'sc')

