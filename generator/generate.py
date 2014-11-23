__author__ = 'ian'
import xml.etree.ElementTree as etree
from script import models
from datetime import date
import re
from xml.etree.ElementTree import Element
from mysql.connector import connect
from mysql.connector.connection import MySQLConnection, MySQLCursor
import json
import os
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "combinatoria.settings")
#os.environ['DJANGO_SETTINGS_MODULE'] = 'combinatoria.settings'
#from django.core.management import setup_environ
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "..combinatoria.settings")

from django.conf import settings

class ParseXML(object):

    def __init__(self, file):
        self.cnx = MySQLConnection()
        self.local_cursor = MySQLCursor()
        self.external_db_cnx = MySQLConnection()
        self.file = file
        self.xml = etree.parse(file).getroot()
        self.dict = self.xml[1]
        self.truncate()
        self.generate_model()


    def connect_to_db(self):
        self.cnx = connect(user='root', password ='ian', host='127.0.0.1',  database='combinatoria') #database='test')
        self.local_cursor = self.cnx.cursor()


    def generate_model(self):
        project = models.Project()
        project.save()
        script = models.Script()
        info_node = self.xml[0]
        script.author = info_node[0].text
        script.title = info_node[1].text
        script.description = info_node[2].text
        script.date = date(year=2007, month=7, day=1)
        script.save()
        project.script_set.add(script)

        act = models.Act()
        act.title = 'conversations'
        act.script = script
        act.save()

        scenes = self.xml.findall('conversation')
        for scene in scenes:
            scene_model = models.Scene()
            scene_model.title = self.dict_value(scene.attrib['title'])
            scene_model.description
            scene_model.act = act
            scene_model.save()
            parts = scene.findall('section')
            for part in parts:
                part_model = models.Part()
                part_model.scene = scene_model
                part_model.name = self.dict_value(part.attrib['keyword'])
                part_model.description = part.attrib['summary']
                part_model.save()
                contents = part.findall('cut')
                for cut in contents:
                    content_model = models.Content()
                    content_model.part = part_model
                    content_model.save()
                    part_model.content_set.add(content_model)
                    self.content_factory(content_model, cut)
                    pass

    def content_factory(self, content, cut):
        type = cut.attrib['type']

        if(type == 'pause'):
            self.process_pause(content, cut)
        elif(type == 'default'):
            self.process_default(content, cut)
        elif(type == 'alternative'):
            self.process_alternative(content, cut)


    def process_pause(self, content, cut):
        scene_name = self.get_scene_name(content.part_id)
        scene_code = self.dict_key(scene_name)
        part_name = models.Part.objects.get(pk=content.part_id).name
        part_code = self.dict_key(part_name)

        pause = models.Group()
        pause.content_id = content.id
        pause.name = scene_code + '_' + part_code + '_' + 'pause'
        pause.save()

        type = models.Type()
        type.name = 'SEQUENCE_SET'
        params = [{'sets':['short', 'medium', 'long']}]
        type.arguments = json.dumps(params)

        type.group_id = pause.id
        type.content_id = content.id
        pause.type_set.add(type)

        pause_txt = models.Line()
        pause_txt.line = 'pause'
        pause_txt.save()
        content.line_set.add(pause_txt)

        pause.line.add(pause_txt)

        library = models.Item()
        library.name = 'library'
        library.content_id = content.id
        library.save()
        pause.item.add(library)
        choices = models.Group()
        choices.content_id = content.id
        choices.name = 'choices'
        choices.save()
        library.group_set.add(choices)

        angles = cut.findall("./shots/angle")
        for angle in angles:
            item = models.Item()
            item.content_id = content.id
            item.name = 'camera_angle'
            item.save()
            source = models.Source()
            source.file = scene_code + '_' + part_code + '_' + angle.attrib['type'] + '.mp4'
            source.mime = 'video/mp4'
            source.duration = float(angle.attrib['length']) * 1000
            source.size = int(angle.attrib['bytes'])
            source.save()
            item_source = models.ItemSource(item=item, source=source, order=0)
            item_source.save()
            #item.source.add(source)
            choices.item.add(item)

        sets = models.Group()
        sets.name = 'sets'
        sets.content_id = content.id
        sets.save()

        short = models.Item()
        short.name = 'short'
        short.content_id = content.id
        short.save()
        sets.item.add(short)

        short_seq_str = cut.find('./sequence[@type="short"]').text
        short_seq = short_seq_str.split(',')
        sequences = [re.split('[+]', items) for items in short_seq]
        i = 0
        for seq in sequences:

            for items in seq:
                items = items.split(',')
                group = models.Group()
                i += 1
                group.name = 'short_' + str(i)
                group.content_id = content.id
                group.save()
                counter = 0
                for item in items:
                    counter += 1
                    source = models.Source.objects.get(file=scene_code + '_' + part_code + '_' + item + '.mp4')
                    group_source = models.GroupSource(group=group, source=source, order=counter)
                    group_source.save()
                    #group.source.add(models.Source.objects.get(file=scene_code + '_' + part_code + '_' + item + '.mp4'))
                short.group_set.add(group)

        medium = models.Item()
        medium.name = 'medium'
        medium.content_id = content.id
        medium.save()
        sets.item.add(medium)

        med_seq_str = cut.find('./sequence[@type="medium"]').text
        med_seq = med_seq_str.split(',')
        sequences = [re.split('[+]', items) for items in med_seq]
        i = 0
        for seq in sequences:
            group = models.Group()
            i += 1
            group.name = 'medium_' + str(i)
            group.content_id = content.id
            group.save()
            counter = 0
            for item in seq:
                counter += 1
                source = models.Source.objects.get(file=scene_code + '_' + part_code + '_' + item + '.mp4')
                group_source = models.GroupSource(group=group, source=source, order=counter)
                group_source.save()
                #source.group_set.add(group)
            medium.group_set.add(group)


        long = models.Item()
        long.name = 'long'
        long.content_id = content.id
        long.save()
        sets.item.add(long)

        long_seq_str = cut.find('./sequence[@type="long"]').text
        long_seq = long_seq_str.split(',')
        sequences = [re.split('[+]', items) for items in long_seq]
        i = 0
        for seq in sequences:
            group = models.Group()
            i += 1
            group.name = 'long_' + str(i)
            group.content_id = content.id
            group._deferred = False
            group.save()
            long.group_set.add(group)
            counter = 0
            for item in seq:
                counter += 1
                source = models.Source.objects.get(file=scene_code + '_' + part_code + '_' + item + '.mp4')
                group_source = models.GroupSource(group=group, source=source, order=counter)
                group_source.save()
                #source.group_set.add(group)

            group.save()
        pause.save()
        content.group_set.add(pause)

        return 0


    def process_default(self, content, cut):
        default = models.Line()
        default.line = cut.find('line').text
        default.speaker = cut.attrib['speaker']
        default.save()
        content.line_set.add(default)
        default_type = models.Type()
        default_type.name = 'DEFAULT'
        default_type.content_id = content.id
        default_type.save()
        default.type_set.add(default_type)

        shots = cut.findall('./shots/angle')
        for shot in shots:
            source = models.Source()
            source.file = cut.find('name').text + '_' + shot.attrib['type'] + '.mp4'
            source.duration = float(shot.attrib['length']) * 1000
            source.mime = 'video/mp4'
            source.size = shot.attrib['bytes']
            source.save()
            line_source = models.LineSource(source=source, line=default)
            line_source.save()
            #default.source.add(source)


    def process_alternative(self, content, cut):
        alternative = self.init_alternative(content, cut)
        alt_type = alternative.type_set.get().name

        print(alt_type)

        if alt_type == 'ALTERNATIVE_FREE':
            self.process_options(content, alternative, cut)

        if alt_type == 'ALTERNATIVE_PAIRED':
            self.process_options(content, alternative, cut)

        if alt_type == 'ALTERNATIVE_PARENT':
            alts = cut.findall('./alternative')
            for alt in alts:
                alt.attrib['speaker'] = cut.attrib['speaker']
                self.process_alternative(content, alt)

        if alt_type == 'ALTERNATIVE_PAIRED_PARENT':
            alts = cut.findall('./alternative')
            for alt in alts:
                alt.attrib['speaker'] = cut.attrib['speaker']
                self.process_alternative(content, alt)

        if alt_type == 'ALTERNATIVE_COMPOUND':
            default = self.write_line(content.id, cut.attrib['speaker'], cut.find('./default/line').text)
            alternative.line.add(default)
            self.process_options(content, alternative, cut)

        if alt_type == 'ALTERNATIVE_PAIRED_MIXED':
            nested = cut.findall('./nested')
            nested[0].attrib['speaker'] = cut.attrib['speaker']
            self.init_alternative(content, nested[0])
            return


    def init_alternative(self, content, cut):
        alternative = models.Group()
        alternative.save()
        type = self.write_alt_type(cut)
        content.type_set.add(type)
        alternative.type_set.add(type)
        alternative.name = type.name.lower()
        alternative.content_id = content.id
        alternative.save()
        return alternative


    def process_options(self, content, alternative, cut):
        options = cut.findall('./option')
        order_pos = 0
        for option in options:
            order_pos += 1
            dialogue = self.write_line(content.id, cut.attrib['speaker'], option.find('./line').text)
            alt_line = models.GroupLine(group=alternative, line=dialogue, order=order_pos)
            alt_line.save()
            #alternative.line.add(dialogue)
            name = option.find('./name').text

            shots = option.findall('./shots/angle')
            for angle in shots:
                source = models.Source()
                source.file = name + '_' + angle.attrib['type'] + '.mp4'
                source.duration = float(angle.attrib['length']) * 1000
                source.mime = 'video/mp4'
                source.size = angle.attrib['bytes']
                source.save()
                line_source = models.LineSource(source=source, line=dialogue)
                line_source.save()
                #dialogue.source.add(source)


    def write_alt_type(self, cut):
        type = models.Type()
        if cut.attrib['alt']:
            subtype = cut.attrib['alt']
            type.name = 'ALTERNATIVE' + '_' + subtype.upper()
        else:
            type.name = 'ALTERNATIVE'

        if 'paired' in subtype:
            position = int(cut.attrib['position'][0:1])
            total = int(cut.attrib['position'][2:])
            next = cut.attrib['next'] if 'next' in cut.attrib else None
            previous = cut.attrib['previous'] if 'previous' in cut.attrib else None
            data = {'pos': position, 'total': total, 'next':next, 'prev': previous}
            data_string = json.dumps(data)

            if 'mixed' in subtype:
                nested_positions = []
                nested = cut.findall('./nested')
                nested_positions.append(int(nested[0].attrib['id']))
                data['nested'] = nested_positions
                data_string = json.dumps(data)

            type.arguments = data_string

        if 'compound' in subtype:
            data = [{'default':1}]
            data_string = json.dumps(data)
            type.arguments = data_string

        type.save()
        return type


    def write_line(self, content_id, speaker, text):
        dialogue = models.Line()
        dialogue.line = text
        dialogue.speaker = speaker
        dialogue.content_id = content_id
        dialogue.save()
        return dialogue


    def dict_value(self, code):
        return self.dict.find('item/.[@code="{0}"]'.format(code)).attrib['content']


    def dict_key(self, code):
        return self.dict.find('item/.[@content="{0}"]'.format(code)).attrib['code']


    def get_scene_name(self, part_id):
        return models.Part.objects.get(pk=part_id).scene.title


    def truncate(self):
        models.Project.objects.all().delete()
        models.Script.objects.all().delete()
        models.Act.objects.all().delete()
        models.Scene.objects.all().delete()
        models.Part.objects.all().delete()
        models.Content.objects.all().delete()
        models.Item.objects.all().delete()
        models.Line.objects.all().delete()
        models.Group.objects.all().delete()
        models.Source.objects.all().delete()
        models.Type.objects.all().delete()
        models.ItemSource.objects.all().delete()
        models.LineSource.objects.all().delete()
        models.GroupSource.objects.all().delete()
        models.GroupItem.objects.all().delete()
        models.GroupLine.objects.all().delete()





print(os.path.dirname(__file__))

def post_process(script):
    paired_args = models.Type.objects.filter(name__contains='PAIRED')
    for type in paired_args:
        print("===================")
        print(type.arguments)
        arg = json.loads(type.arguments)
        #print(arg)
        act_id = models.Act.objects.get(title='conversations').id

        if arg['prev'] is not None:
            prev_list = arg['prev'].split('_')
            scene_id = models.Scene.objects.get(title=script.dict_value(prev_list[0])).id
            part_id = models.Part.objects.get(scene_id=scene_id, name=script.dict_value(prev_list[1])).id
            contents = models.Content.objects.filter(part_id=part_id)
            content_id = contents[int(prev_list[2])-1].id
            arg['prev'] = str(content_id) # str(act_id) + ':' + str(scene_id) + ':' + str(part_id) + ':' + str(content_id)
            print('prev: ' + arg['prev'])
            #new_args = json.dumps(arg)

            type.arguments = json.dumps(arg)
            type.save()
            pass


        if arg['next'] is not None:
            next_list = arg['next'].split('_')
            scene_id = models.Scene.objects.get(title=script.dict_value(next_list[0])).id
            part_id = models.Part.objects.get(scene_id=scene_id, name=script.dict_value(next_list[1])).id
            contents = models.Content.objects.filter(part_id=part_id)
            content_id = contents[int(next_list[2])-1].id
            arg['next'] = str(content_id) #str(act_id) + ':' + str(scene_id) + ':' + str(part_id) + ':' + str(content_id)
            print('next: ' + arg['next'])
            type.arguments = json.dumps(arg)
            type.save()
            pass




    pass

gen = ParseXML('/opt/combinatoria/xml/Jane.xml')
post_process(gen)



#gen = ParseXML('/opt/combinatoria/xml/JanePairedMixed.xml')