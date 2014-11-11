__author__ = 'ian'
import xml.etree.ElementTree as etree
from script import models
from datetime import date
import re
from xml.etree.ElementTree import Element
from mysql.connector import connect
from mysql.connector.connection import MySQLConnection, MySQLCursor
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

        #self.connect_to_db()
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
        #headerPath = root.find('File/.[@id="{0}"]'.format(headerRef)).attrib['name']
        #node = info_node['author']
        script.author = info_node[0].text
        script.title = info_node[1].text
        script.description = info_node[2].text
        script.date = date(year=2007,month=7, day=1)
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

        pass

    def content_factory(self, content, cut):
        type = cut.attrib['type']

        if(type == 'pause'):
            self.process_pause(content, cut)
        elif(type == 'default'):
            self.process_default(content, cut)
        elif(type == 'alternative'):
            pass


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
        type.group_id = pause.id
        type.content_id = content.id
        pause.type_set.add(type)

        pause_txt = models.Line()
        pause_txt.line = 'pause'
        pause_txt.save()
        content.line_set.add(pause_txt)

        pause.line.add(pause_txt)
        #pause.line.add(pause_txt)

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
            item.save()
            source = models.Source()
            source.file = scene_code + '_' + part_code + '_' + angle.attrib['type'] + '.mp4'
            source.mime = 'video/mp4'
            source.duration = float(angle.attrib['length']) * 1000
            source.size = int(angle.attrib['bytes'])
            source.save()
            item.source.add(source)
            choices.item.add(item)
            #choices.source_set.add(source)

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
                for item in items:
                    group.source.add(models.Source.objects.get(file=scene_code + '_' + part_code + '_' + item + '.mp4'))
                short.group_set.add(group)


        medium = models.Item()
        medium.name = 'medium'
        medium.content_id = content.id
        medium.save()

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

            for item in seq:
                source = models.Source.objects.get(file=scene_code + '_' + part_code + '_' + item + '.mp4')
                source.group_set.add(group)
            medium.group_set.add(group)


        long = models.Item()
        long.name = 'long'
        long.content_id = content.id
        long.save()

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

            for item in seq:
                source = models.Source.objects.get(file=scene_code + '_' + part_code + '_' + item + '.mp4')
                source.group_set.add(group)

            group.save()
        pause.save()
        content.group_set.add(pause)

        return 0

    def insert_source(self, group_id, source_id):
        # insert_source_query = ("INSERT into script_group_source group_id, source_id VALUES()".format())
        # cmd = self.cnx.cmd_query(insert_source_query)
        #
        # for row in self.cnx.get_rows()[0]:
        #     print(row)

        #self.insert_source_id(source_id)


        add_source = ("INSERT into script_group_source "#"INSERT IGNORE into script_group_source "
                      "(group_id, source_id) "
                      "VALUES (%(group_id)s, %(source_id)s)")

        source_data = {
            'group_id': group_id,
            'source_id': source_id
        }
        self.local_cursor.execute(add_source, source_data)
        self.cnx.commit()


    def insert_source_id(self, source_id):
        add_source = ("INSERT IGNORE into Source "
                          "(id) "
                          "VALUES(%(source_id)s)")

        source_data = {
                'source_id': source_id
        }

        self.local_cursor.execute(add_source, source_data)
        self.cnx.commit()
            #source.group_set.add(group)
            #group.save()

        pass

    def reorder(self, pks):
        re_order = ("UPDATE group_id from script_group_source"
                     "where group_id={0}"
                     "ORDER BY(pks)")

    def process_default(self, content, cut):
        default = models.Line()
        default.line = cut.find('line').text
        default.speaker = cut.attrib['speaker']
        content.line_set.add(default)
        default.save()

    def process_alternative(self,content,cut):
        pass

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


print(os.path.dirname(__file__))
gen = ParseXML('/opt/combinatoria/xml/Jane.xml')

