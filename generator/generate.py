__author__ = 'ian'
import xml.etree.ElementTree as etree
from script import models
from datetime import date
from xml.etree.ElementTree import Element

import os
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "combinatoria.settings")
#os.environ['DJANGO_SETTINGS_MODULE'] = 'combinatoria.settings'

#from django.core.management import setup_environ


#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "..combinatoria.settings")

from django.conf import settings
class ParseXML(object):

    def __init__(self, file):
        self.file = file
        self.xml = etree.parse(file).getroot()
        self.dict = self.xml[1]
        self.truncate()
        self.generate_model()


    def generate_model(self):
        script = models.Script()
        info_node = self.xml[0]
        #headerPath = root.find('File/.[@id="{0}"]'.format(headerRef)).attrib['name']
        #node = info_node['author']
        script.author = info_node[0].text
        script.title = info_node[1].text
        script.description = info_node[2].text
        script.date = date(year=2007,month=7, day=1)
        script.save()

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
        pause = models.Group()
        pause.save()
        type = models.Type()
        type.name = 'SEQUENCE'
        type.group_id = pause.id
        pause.type_set.add(type)
        angles = cut.findall("./shots/angle")

        scene_name = self.get_scene_name(content.part_id)
        scene_code = self.dict_key(scene_name)
        part_name = models.Part.objects.get(pk=content.part_id).name
        part_code = self.dict_key(part_name)
        for angle in angles:
            source = models.Source()
            source.file = scene_code + '_' + part_code + '_' + angle.attrib['type']
            pass


        pause_txt = models.Line()
        pause_txt.line = 'pause'
        content.line_set.add(pause_txt)
        pause_txt.save()

        pause.line.add(pause_txt)

        seq_group1 = models.Group()
        seq_group1.name = 'surprise'
        seq_group1.save()
        seq_group1.line.create(line='what')
        seq_group1.line.create(line='the')
        seq_group1.line.create(line='fuck')

        seq_group2 = models.Group()
        seq_group2.name = 'love'
        seq_group2.save()
        seq_group2.line.create(line='Reyhan')
        seq_group2.line.create(line='is')
        seq_group2.line.create(line='fab')

        seq_group3 = models.Group()
        seq_group3.name = 'bedtime'
        seq_group3.save()
        seq_group3.line.create(line='Ian')
        seq_group3.line.create(line='is')
        seq_group3.line.create(line='tired')

        seq_options = models.Item()
        seq_options.name = 'sequeunces'
        seq_options.save()
        seq_options.group_set.add(seq_group1, seq_group2, seq_group3)
        pause.item.add(seq_options)

        pause.save()
        content.group_set.add(pause)

        return 0


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

