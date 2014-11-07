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
                part_model.title = self.dict_value(part.attrib['keyword'])
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
        # print(cut.attrib['type'])
        # rc ={
        #     'pause': self.process_pause(content, cut),
        #     'default': self.process_default(content, cut),
        #     'alternative': models.Alternative()
        # }.get(cut.attrib['type'])
        #return rc



    def process_pause(self, content, cut):
        pause = models.Group()
        pause.type_set.create(name='SEQUENCE')
        #line = models.Line(line='Pause')
        #line.line = 'Pause'
        #line.save()
        #pause.group = models.Group()
        #pause.group.save()
        pause.line.create(line='Pause')
        pause.content = content.id

        seq_group1 = models.Group()
        seq_group1.name = 'surprise'
        seq_group1.item.create(line='what')
        seq_group1.item.create(line='the')
        seq_group1.item.create(line='fuck')

        seq_group2 = models.Group()
        seq_group2.name = 'love'
        seq_group2.item.create(line='Reyhan')
        seq_group2.item.create(line='is')
        seq_group2.item.create(line='fab')

        seq_group3 = models.Group()
        seq_group3.name = 'bedtime'
        #seq_group3.item.add(models.LineItem(line='Ian'))
        seq_group3.item.create(line='Ian')
        seq_group3.item.create(line='is')
        seq_group3.item.create(line='tired')

        seq_options = models.Item()
        seq_options.name = 'sequeunces'
        seq_options.group_set.add(seq_group1, seq_group2, seq_group3)
        pause.item.add(seq_options)
        pause.save()

        return 0


    def process_default(self, content, cut):
        default = models.Line()
        test = cut.find('line')
        default.line = cut.find('line').text
        default.speaker = cut.attrib['speaker']
        content.lineitem_set.add(default)
        #content.lineitem_set.

    def process_alternative(self,content,cut):
        pass

    def dict_value(self, code):
        return self.dict.find('item/.[@code="{0}"]'.format(code)).attrib['content']


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


print(os.path.dirname(__file__))
gen = ParseXML('/opt/combinatoria/xml/Jane.xml')

